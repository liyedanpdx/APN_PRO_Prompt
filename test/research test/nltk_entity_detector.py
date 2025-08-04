import nltk
import re
from typing import List, Dict, Any
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk.tree import Tree

class NLTKEntityDetector:
    def __init__(self):
        self._download_nltk_data()
        
        self.job_title_patterns = [
            r'\b(?:engineer|developer|analyst|manager|director|specialist|coordinator|consultant|architect|designer|scientist|researcher|technician|administrator|executive|officer|supervisor|lead|senior|junior|principal|staff)\b',
            r'\b(?:software|backend|frontend|full.?stack|data|machine learning|ai|web|mobile|devops|qa|quality assurance|product|project|sales|marketing|hr|human resources|finance|accounting|operations|customer service)\s+(?:engineer|developer|analyst|manager|director|specialist|coordinator|consultant|architect|designer|scientist|researcher|technician|administrator|executive|officer)\b',
            r'\b(?:ceo|cto|cfo|coo|vp|vice president|president|founder|co.?founder)\b'
        ]
        
        self.experience_patterns = [
            r'\b(?:\d+|\w+)\s*(?:\+|\-|\s)*\s*(?:years?|yrs?|year)\s*(?:of\s*)?(?:experience|exp)\b',
            r'\b(?:more than|over|above|at least|minimum|min)\s*(?:\d+|\w+)\s*(?:years?|yrs?)\b',
            r'\b(?:\d+|\w+)\s*(?:to|\-)\s*(?:\d+|\w+)\s*(?:years?|yrs?)\b',
            r'\b(?:experience|exp)\s*(?:of\s*)?(?:\d+|\w+)\s*(?:years?|yrs?)\b'
        ]
        
        self.industry_keywords = [
            'technology', 'tech', 'software', 'it', 'information technology',
            'finance', 'financial', 'banking', 'investment', 'insurance',
            'healthcare', 'medical', 'pharmaceutical', 'biotech',
            'retail', 'e-commerce', 'ecommerce', 'consumer',
            'manufacturing', 'automotive', 'aerospace', 'defense',
            'education', 'academic', 'university', 'school',
            'media', 'advertising', 'marketing', 'entertainment',
            'consulting', 'professional services', 'legal',
            'real estate', 'construction', 'architecture',
            'energy', 'oil', 'gas', 'renewable', 'utilities',
            'telecommunications', 'telecom', 'networking',
            'gaming', 'sports', 'hospitality', 'travel'
        ]
        
        self.skills_patterns = [
            r'\b(?:python|java|javascript|c\+\+|c#|php|ruby|go|rust|swift|kotlin|typescript|scala|r|matlab|sql|html|css)\b',
            r'\b(?:react|angular|vue|node|express|django|flask|spring|laravel|rails)\b',
            r'\b(?:aws|azure|gcp|docker|kubernetes|jenkins|git|linux|windows|mac)\b',
            r'\b(?:machine learning|ml|ai|artificial intelligence|deep learning|neural networks|nlp|computer vision)\b',
            r'\b(?:agile|scrum|devops|ci/cd|testing|debugging|problem solving|teamwork|communication|leadership)\b'
        ]

    def _download_nltk_data(self):
        required_data = ['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
        
        for data in required_data:
            try:
                nltk.data.find(f'tokenizers/{data}')
            except LookupError:
                try:
                    nltk.download(data, quiet=True)
                except:
                    pass

    def detect_entities(self, text: str) -> Dict[str, Any]:
        result = {
            "result": [
                {"label": "Location", "containsCriteria": self._detect_location(text)},
                {"label": "Job Title", "containsCriteria": self._detect_job_title(text)},
                {"label": "Years of Experience", "containsCriteria": self._detect_experience(text)},
                {"label": "Industry", "containsCriteria": self._detect_industry(text)},
                {"label": "Skills", "containsCriteria": self._detect_skills(text)}
            ]
        }
        
        return result

    def _detect_location(self, text: str) -> bool:
        try:
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            tree = ne_chunk(pos_tags)
            
            for subtree in tree:
                if isinstance(subtree, Tree):
                    if subtree.label() in ['GPE', 'LOCATION']:
                        return True
        except:
            pass
        
        location_patterns = [
            r'\b(?:remote|onsite|hybrid|work from home|wfh)\b',
            r'\b(?:city|state|country|region|area|location|based in|located in)\b',
            r'\b(?:new york|san francisco|london|paris|tokyo|beijing|singapore|sydney|toronto|berlin|amsterdam|dublin|zurich|stockholm|copenhagen|oslo|helsinki|vienna|prague|warsaw|budapest|bucharest|sofia|athens|rome|madrid|barcelona|lisbon|brussels|luxembourg|geneva|milan|frankfurt|munich|cologne|hamburg|stuttgart|dusseldorf|hannover|leipzig|dresden|nuremberg|bremen|dortmund|essen|duisburg|bochum|wuppertal|bielefeld|bonn|mannheim|karlsruhe|wiesbaden|augsburg|chemnitz|kiel|halle|magdeburg|freiburg|krefeld|mainz|oberhausen|erfurt|rostock|kassel|hagen|potsdam|saarbrucken|hamm|ludwigshafen|mulheim|oldenburg|osnabruck|leverkusen|solingen|heidelberg|darmstadt|paderborn|regensburg|wurzburg|gottingen|recklinghausen|heilbronn|ingolstadt|bottrop|offenbach|pforzheim|bremerhaven|remscheid|fürth|reutlingen|koblenz|bergisch gladbach|jena|trier|moers|siegen|hildesheim|salzgitter|cottbus)\b'
        ]
        
        text_lower = text.lower()
        for pattern in location_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False

    def _detect_job_title(self, text: str) -> bool:
        text_lower = text.lower()
        
        for pattern in self.job_title_patterns:
            if re.search(pattern, text_lower):
                return True
        
        try:
            tokens = word_tokenize(text_lower)
            pos_tags = pos_tag(tokens)
            
            job_pos_patterns = ['NN', 'NNS', 'NNP', 'NNPS']
            job_keywords = ['position', 'role', 'job', 'opening', 'opportunity', 'hire', 'recruit', 'looking for', 'seeking', 'wanted', 'needed']
            
            for i, (word, pos) in enumerate(pos_tags):
                if word in job_keywords and i < len(pos_tags) - 1:
                    next_word, next_pos = pos_tags[i + 1]
                    if next_pos in job_pos_patterns:
                        return True
        except:
            pass
        
        return False

    def _detect_experience(self, text: str) -> bool:
        text_lower = text.lower()
        
        for pattern in self.experience_patterns:
            if re.search(pattern, text_lower):
                return True
        
        try:
            tokens = word_tokenize(text_lower)
            
            experience_indicators = ['experience', 'exp', 'background', 'years', 'yrs', 'seasoned', 'veteran', 'expert']
            number_words = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'fifteen', 'twenty']
            
            for i, token in enumerate(tokens):
                if token in experience_indicators:
                    if i > 0 and (tokens[i-1].isdigit() or tokens[i-1] in number_words):
                        return True
                    if i < len(tokens) - 1 and (tokens[i+1].isdigit() or tokens[i+1] in number_words):
                        return True
        except:
            pass
        
        return False

    def _detect_industry(self, text: str) -> bool:
        text_lower = text.lower()
        
        for keyword in self.industry_keywords:
            if keyword in text_lower:
                return True
        
        industry_patterns = [
            r'\b(?:department|division|sector|industry|field|domain|vertical|company|corporation|firm|business|organization|startup|enterprise)\b'
        ]
        
        for pattern in industry_patterns:
            if re.search(pattern, text_lower):
                return True
        
        try:
            tokens = word_tokenize(text_lower)
            pos_tags = pos_tag(tokens)
            
            industry_pos_patterns = ['NN', 'NNS', 'NNP', 'NNPS']
            industry_indicators = ['industry', 'sector', 'field', 'domain', 'market', 'business']
            
            for i, (word, pos) in enumerate(pos_tags):
                if word in industry_indicators and i > 0:
                    prev_word, prev_pos = pos_tags[i - 1]
                    if prev_pos in industry_pos_patterns:
                        return True
        except:
            pass
        
        return False

    def _detect_skills(self, text: str) -> bool:
        text_lower = text.lower()
        
        for pattern in self.skills_patterns:
            if re.search(pattern, text_lower):
                return True
        
        skills_keywords = [
            'skills', 'expertise', 'proficient', 'experience with', 'knowledge of',
            'familiar with', 'background in', 'competency', 'ability', 'capable',
            'skilled', 'experienced', 'expert in', 'specializing', 'specialized'
        ]
        
        for keyword in skills_keywords:
            if keyword in text_lower:
                return True
        
        try:
            tokens = word_tokenize(text_lower)
            pos_tags = pos_tag(tokens)
            
            skill_indicators = ['with', 'using', 'in', 'on', 'for']
            tech_pos_patterns = ['NN', 'NNS', 'NNP', 'NNPS']
            
            for i, (word, pos) in enumerate(pos_tags):
                if word in skill_indicators and i < len(pos_tags) - 1:
                    next_word, next_pos = pos_tags[i + 1]
                    if next_pos in tech_pos_patterns and len(next_word) > 2:
                        return True
        except:
            pass
        
        return False


def test_nltk_detector():
    detector = NLTKEntityDetector()
    
    test_sentences = [
        "We are looking for a backend engineer for our financial department. We hope this candidate have more than 5 years",
        "Senior Python developer needed in New York with 3+ years experience in fintech",
        "Remote software architect position available for blockchain industry",
        "Marketing manager role in healthcare sector, minimum 7 years experience required",
        "Looking for a data scientist with machine learning skills and SQL expertise",
        "Frontend developer position in San Francisco, React and JavaScript required",
        "Project manager needed for construction company, 5-8 years experience",
        "DevOps engineer wanted with AWS and Docker experience in tech startup"
    ]
    
    print("=== NLTK Entity Detection Results ===\n")
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"Test {i}: {sentence}")
        result = detector.detect_entities(sentence)
        
        for entity in result["result"]:
            status = "Yes" if entity["containsCriteria"] else "No"
            print(f"  {entity['label']}: {status}")
        print()


if __name__ == "__main__":
    test_nltk_detector()