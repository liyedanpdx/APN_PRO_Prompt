import re
from typing import Dict, Any

class SimpleEntityDetector:
    def __init__(self):
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
        
        self.location_patterns = [
            r'\b(?:remote|onsite|hybrid|work from home|wfh)\b',
            r'\b(?:city|state|country|region|area|location|based in|located in)\b',
            r'\b(?:new york|san francisco|london|paris|tokyo|beijing|singapore|sydney|toronto|berlin|amsterdam|dublin|seattle|boston|chicago|los angeles|miami|atlanta|denver|austin|portland|vancouver|montreal|calgary|mexico city|sao paulo|buenos aires|madrid|barcelona|rome|milan|zurich|stockholm|copenhagen|oslo|helsinki|vienna|prague|warsaw|budapest|bucharest|sofia|athens|lisbon|brussels|luxembourg|geneva|frankfurt|munich|cologne|hamburg|stuttgart|dusseldorf)\b'
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
            'gaming', 'sports', 'hospitality', 'travel',
            'department', 'division', 'sector', 'industry', 'field', 'domain'
        ]
        
        self.skills_patterns = [
            r'\b(?:python|java|javascript|c\+\+|c#|php|ruby|go|rust|swift|kotlin|typescript|scala|r|matlab|sql|html|css)\b',
            r'\b(?:react|angular|vue|node|express|django|flask|spring|laravel|rails)\b',
            r'\b(?:aws|azure|gcp|docker|kubernetes|jenkins|git|linux|windows|mac)\b',
            r'\b(?:machine learning|ml|ai|artificial intelligence|deep learning|neural networks|nlp|computer vision)\b',
            r'\b(?:agile|scrum|devops|ci/cd|testing|debugging|problem solving|teamwork|communication|leadership)\b'
        ]
        
        self.skills_keywords = [
            'skills', 'expertise', 'proficient', 'experience with', 'knowledge of',
            'familiar with', 'background in', 'competency', 'ability', 'capable',
            'skilled', 'experienced', 'expert in', 'specializing', 'specialized'
        ]

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
        text_lower = text.lower()
        
        for pattern in self.location_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False

    def _detect_job_title(self, text: str) -> bool:
        text_lower = text.lower()
        
        for pattern in self.job_title_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False

    def _detect_experience(self, text: str) -> bool:
        text_lower = text.lower()
        
        for pattern in self.experience_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False

    def _detect_industry(self, text: str) -> bool:
        text_lower = text.lower()
        
        for keyword in self.industry_keywords:
            if keyword in text_lower:
                return True
        
        return False

    def _detect_skills(self, text: str) -> bool:
        text_lower = text.lower()
        
        for pattern in self.skills_patterns:
            if re.search(pattern, text_lower):
                return True
        
        for keyword in self.skills_keywords:
            if keyword in text_lower:
                return True
        
        return False


def test_simple_detector():
    detector = SimpleEntityDetector()
    
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
    
    print("=== Simple Regex Entity Detection Results ===\n")
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"Test {i}: {sentence}")
        result = detector.detect_entities(sentence)
        
        for entity in result["result"]:
            status = "Yes" if entity["containsCriteria"] else "No"
            print(f"  {entity['label']}: {status}")
        print()


if __name__ == "__main__":
    test_simple_detector()