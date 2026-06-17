"""Enhanced entity extraction with NER and scoring"""

import re
import logging
from typing import List, Dict
from collections import Counter
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=2)

class EntityExtractor:
    """Extract and score entities from text using NER and keyword matching"""

    # Comprehensive keyword patterns
    COUNTRY_PATTERNS = [
        r'\b(United States|United Kingdom|South Korea|Saudi Arabia|South Africa|New Zealand|Costa Rica|Middle East|Persian Gulf|Strait of Hormuz)\b',
        r'\b(Afghanistan|Albania|Algeria|Andorra|Angola|Argentina|Armenia|Australia|Austria|Azerbaijan|'
        r'Bahamas|Bahrain|Bangladesh|Barbados|Belarus|Belgium|Belize|Benin|Bhutan|Bolivia|Bosnia|Botswana|'
        r'Brazil|Brunei|Bulgaria|Burkina|Burundi|Cambodia|Cameroon|Canada|Cape Verde|Chad|Chile|China|Colombia|'
        r'Comoros|Congo|Croatia|Cuba|Cyprus|Czechia|Denmark|Djibouti|Dominica|Dominican|Ecuador|Egypt|'
        r'El Salvador|Equatorial|Eritrea|Estonia|Eswatini|Ethiopia|Fiji|Finland|France|Gabon|Gambia|Georgia|'
        r'Germany|Ghana|Greece|Grenada|Guatemala|Guinea|Guyana|Haiti|Honduras|Hungary|Iceland|India|Indonesia|'
        r'Iran|Iraq|Ireland|Israel|Italy|Jamaica|Japan|Jordan|Kazakhstan|Kenya|Kiribati|Korea|Kosovo|Kuwait|'
        r'Kyrgyzstan|Laos|Latvia|Lebanon|Lesotho|Liberia|Libya|Liechtenstein|Lithuania|Luxembourg|Madagascar|'
        r'Malawi|Malaysia|Maldives|Mali|Malta|Marshall|Mauritania|Mauritius|Mexico|Micronesia|Moldova|Monaco|'
        r'Mongolia|Montenegro|Morocco|Mozambique|Myanmar|Namibia|Nauru|Nepal|Netherlands|Nicaragua|Niger|Nigeria|'
        r'North Macedonia|Norway|Oman|Pakistan|Palau|Palestine|Panama|Papua|Paraguay|Peru|Philippines|Poland|'
        r'Portugal|Qatar|Romania|Russia|Rwanda|Saint|Samoa|San Marino|Sao Tome|Senegal|Serbia|Seychelles|'
        r'Sierra Leone|Singapore|Slovakia|Slovenia|Solomon|Somalia|South Sudan|Spain|Sri Lanka|Sudan|Suriname|'
        r'Sweden|Switzerland|Syria|Taiwan|Tajikistan|Tanzania|Thailand|Timor|Togo|Tonga|Trinidad|Tunisia|Turkey|'
        r'Turkmenistan|Tuvalu|Uganda|Ukraine|UAE|Uruguay|Uzbekistan|Vanuatu|Vatican|Venezuela|Vietnam|Yemen|Zambia|Zimbabwe|'
        r'US|UK|EU|USA|USSR|Israel|Palestine|Iraq|Syria|Yemen|Lebanon|Jordan|Egypt|Saudi|Oman|Qatar|Bahrain|Kuwait|'
        r'Houthi|Tamil|Kashmir|Xinjiang)\b'
    ]

    PERSON_PATTERNS = [
        r'\b(Vladimir Putin|Xi Jinping|Joe Biden|Donald Trump|Narendra Modi|Emmanuel Macron|Angela Merkel|'
        r'Benjamin Netanyahu|Hassan Rouhani|Recep Tayyip Erdogan|Mohammad bin Salman|Ayatollah Khomeini|Ayatollah Khamenei|'
        r'Kamala Harris|Mike Pence|Nancy Pelosi|Mitch McConnell|Antony Blinken|Kaja Kallas|'
        r'Volodymyr Zelensky|Olaf Scholz|Giorgia Meloni|Justin Trudeau|Mark Rutte|Liz Truss|Rishi Sunak|'
        r'Javier Milei|Pedro Sanchez|Keir Starmer|Raisi|Rouhani|Khamenei|Abbas|Sisi|MBS|'
        r'Sunak|Starmer|Modi|Macron|Scholz|Meloni|Erdogan|Netanyahu|'
        r'Biden|Trump|Putin|Xi|Zelensky|Blinken)\b',
        r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',  # Names with 2-3 parts - more liberal
        r'\b(President|Prime Minister|King|Queen|Emperor|General|Colonel|Minister|Senator|'
        r'Secretary|Director|Chairman|CEO|Mayor|Governor|Ambassador|Pope|Rabbi|Imam|Sheikh|Chief|Leader|'
        r'Foreign Secretary|Defense Secretary|National Security Advisor)\b'
    ]

    ORG_PATTERNS = [
        r'\b(United Nations|UN|NATO|UNESCO|WHO|FBI|CIA|NSA|Pentagon|Congress|Parliament|Senate|House of Commons|House of Lords|'
        r'Supreme Court|International Court|European Union|African Union|Arab League|ASEAN|OPEC|Gulf Cooperation Council|'
        r'World Bank|IMF|UNICEF|Red Cross|Red Crescent|Doctors Without Borders|Amnesty International|Human Rights Watch|'
        r'Google|Microsoft|Apple|Amazon|Tesla|Facebook|Meta|Twitter|YouTube|Reuters|Associated Press|'
        r'BBC|CNN|Fox News|MSNBC|The Guardian|The New York Times|The Washington Post|AFP|Al Jazeera|BBC News|'
        r'Hindustan Times|India Today|The Times of India|Daily Mail|Reuters|AP News|IRNA|IRINN|Saudi Press Agency|'
        r'Houthi|Taliban|ISIS|Al Qaeda|PKK|IDF|Iranian Revolutionary Guard|IRGC)\b'
    ]

    # Geopolitical keywords for context
    GEOPOLITICAL_KEYWORDS = [
        'war', 'conflict', 'peace', 'ceasefire', 'treaty', 'agreement', 'nuclear', 'uranium',
        'sanctions', 'diplomatic', 'negotiations', 'alliance', 'coalition', 'military', 'defense',
        'attack', 'strike', 'missile', 'weapons', 'security', 'threat', 'crisis', 'tension',
        'strait', 'gulf', 'region', 'terrorism', 'extremist', 'insurgent', 'rebellion'
    ]

    # Location keywords
    LOCATION_PATTERNS = [
        r'\b(Middle East|Persian Gulf|Strait of Hormuz|Red Sea|Mediterranean|Arabian Peninsula|'
        r'Levant|Fertile Crescent|Horn of Africa|East Africa|North Africa|Central Asia|South Asia|'
        r'Southeast Asia|East Asia|Europe|Americas|Pacific|Atlantic|Indian Ocean|Persian Gulf|'
        r'Gulf of Aden|Suez Canal|Kashmir|Crimea|Syria|Yemen|Iraq|Afghanistan|Lebanon|Palestine|'
        r'Gaza|West Bank|Sinai|Eastern Europe|Caucasus|Balkans)\b'
    ]

    @staticmethod
    async def extract_and_score_entities(text: str) -> Dict:
        """Extract entities and score them by frequency, position, and importance"""

        logger.info("Starting enhanced entity extraction with NER...")

        entities_dict = {}

        # 1. Extract entities using patterns
        entities_dict['COUNTRY'] = EntityExtractor._extract_by_patterns(text, EntityExtractor.COUNTRY_PATTERNS, 'COUNTRY')
        entities_dict['PERSON'] = EntityExtractor._extract_by_patterns(text, EntityExtractor.PERSON_PATTERNS, 'PERSON')
        entities_dict['ORG'] = EntityExtractor._extract_by_patterns(text, EntityExtractor.ORG_PATTERNS, 'ORG')
        entities_dict['LOCATION'] = EntityExtractor._extract_by_patterns(text, EntityExtractor.LOCATION_PATTERNS, 'LOCATION')

        # 2. Score entities
        scored_entities = []
        for entity_type, entities in entities_dict.items():
            for entity, freq in entities:
                score = EntityExtractor._calculate_entity_score(entity, freq, text, entity_type)
                scored_entities.append({
                    "name": entity,
                    "type": entity_type,
                    "frequency": freq,
                    "importance_score": score
                })

        # 3. Deduplicate similar entities
        scored_entities = EntityExtractor.deduplicate_similar(scored_entities)

        # 4. Sort by importance and return top N
        scored_entities.sort(key=lambda x: x["importance_score"], reverse=True)
        top_entities = scored_entities[:25]  # Top 25 entities

        logger.info(f"Extracted {len(top_entities)} scored entities from {sum(len(v) for v in entities_dict.values())} total matches")

        return {
            "total_count": len(top_entities),
            "entities": top_entities,
            "summary": f"Found {len(top_entities)} key entities (Countries: {len([e for e in top_entities if e['type']=='COUNTRY'])}, People: {len([e for e in top_entities if e['type']=='PERSON'])}, Locations: {len([e for e in top_entities if e['type']=='LOCATION'])}, Orgs: {len([e for e in top_entities if e['type']=='ORG'])})"
        }

    @staticmethod
    def _extract_by_patterns(text: str, patterns: list, entity_type: str) -> list:
        """Extract entities by regex patterns and return with frequency"""
        matches = []

        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            matches.extend(found)

        # Normalize and count frequency
        normalized = {}
        for match in matches:
            key = match.strip()
            normalized[key] = normalized.get(key, 0) + 1

        # Return as sorted list by frequency
        return sorted(normalized.items(), key=lambda x: x[1], reverse=True)

    @staticmethod
    def _calculate_entity_score(entity: str, frequency: int, text: str, entity_type: str) -> float:
        """Calculate importance score for entity"""

        score = 0.0

        # Frequency score (0-35)
        max_freq = min(frequency, 15)
        frequency_score = (max_freq / 15) * 35
        score += frequency_score

        # Position score (0-35) - earlier mentions = higher score
        first_pos = text.lower().find(entity.lower())
        if first_pos != -1:
            position_ratio = first_pos / len(text)
            position_score = (1 - position_ratio) * 35
            score += position_score

        # Entity type score (0-30) - importance by type
        type_scores = {
            'PERSON': 30,      # Leaders/key people highly important
            'COUNTRY': 25,     # Countries/regions important
            'LOCATION': 22,    # Geographic regions
            'ORG': 15         # Organizations
        }
        score += type_scores.get(entity_type, 10)

        # Geopolitical context bonus (0-10)
        geo_context = sum(1 for kw in EntityExtractor.GEOPOLITICAL_KEYWORDS if kw.lower() in text.lower())
        if geo_context > 0:
            context_bonus = min(10, geo_context / 5)
            score += context_bonus

        # Normalize to 0-100
        return min(100, round(score, 1))

    @staticmethod
    def deduplicate_similar(entities: list) -> list:
        """Deduplicate similar entity names (e.g., USA, US, United States)"""

        # Mapping of similar entities
        aliases = {
            'usa': ['us', 'united states', 'u.s.', 'u.s.a.', 'american', 'america'],
            'uk': ['united kingdom', 'great britain', 'british', 'britain'],
            'russia': ['russian federation', 'ussr', 'moscow'],
            'israel': ['israeli', 'zionist', 'tel aviv'],
            'iran': ['iranian', 'persia', 'tehran'],
            'china': ['chinese', 'prc', 'peoples republic', 'beijing'],
            'korea': ['north korea', 'south korea', 'korean'],
            'parliament': ['congress', 'senate', 'house', 'parliament'],
            'united nations': ['un', 'u.n.'],
            'nato': ['north atlantic treaty organization'],
            'middle east': ['middle eastern', 'mideast'],
            'persian gulf': ['gulf', 'arabian gulf']
        }

        # Group similar entities
        seen = {}
        for entity in entities:
            entity_lower = entity['name'].lower().strip()

            # Check if this is an alias of a known entity
            canonical = None
            for primary, alt_list in aliases.items():
                if entity_lower == primary or entity_lower in alt_list:
                    canonical = primary
                    break

            if canonical:
                if canonical not in seen:
                    seen[canonical] = entity.copy()
                    seen[canonical]['name'] = canonical.title()
                else:
                    # Keep the one with higher score
                    if entity['importance_score'] > seen[canonical]['importance_score']:
                        seen[canonical] = entity.copy()
                        seen[canonical]['name'] = canonical.title()
            else:
                if entity_lower not in seen:
                    seen[entity_lower] = entity

        return list(seen.values())
