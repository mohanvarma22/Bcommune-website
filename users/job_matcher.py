# job_matcher.py
from fuzzywuzzy import fuzz

class InternshipMatcher:
    def __init__(self):
        self.weights = {
            'skills_match': 0.40,
            'experience_match': 0.30,
            'education_match': 0.30
        }

    def calculate_match(self, application, internship):
        scores = {
            'skills_match': self._calculate_skills_score(application.skills, internship.required_skills),
            'experience_match': self._calculate_experience_score(application.work_experience, internship.min_experience),
            'education_match': self._calculate_education_score(application.degree, internship.required_qualification)
        }

        weighted_score = sum(scores[key] * self.weights[key] for key in scores)
        return {
            'overall_score': round(weighted_score, 1),
            'detailed_scores': scores,
            'matching_skills': self._get_matching_skills(application.skills, internship.required_skills),
            'missing_skills': self._get_missing_skills(application.skills, internship.required_skills)
        }

    def _calculate_skills_score(self, applicant_skills, job_skills):
        if not job_skills:
            return 0
            
        applicant_skills = set(s.strip().lower() for s in applicant_skills.split(','))
        job_skills = set(s.strip().lower() for s in job_skills.split(','))

        matches = sum(
            max(fuzz.ratio(j_skill, a_skill) for a_skill in applicant_skills) > 80
            for j_skill in job_skills
        )
        return (matches / len(job_skills)) * 100

    def _calculate_experience_score(self, applicant_exp, required_exp):
        if not required_exp:
            return 100

        if applicant_exp >= required_exp * 1.5:
            return max(50, 100 * (required_exp * 1.5) / applicant_exp)
        
        if applicant_exp >= required_exp:
            return 100

        return (applicant_exp / required_exp) * 100

    def _calculate_education_score(self, applicant_edu, required_edu):
        education_levels = {
            'diploma': 2,
            'bachelor': 3,
            'masters': 4,
            'phd': 5
        }

        applicant_level = education_levels.get(applicant_edu.lower(), 0)
        required_level = education_levels.get(required_edu.lower(), 0)

        if applicant_level >= required_level:
            return 100
        return (applicant_level / required_level) * 100 if required_level else 0

    def _get_matching_skills(self, applicant_skills, job_skills):
        if not applicant_skills or not job_skills:
            return []
            
        applicant_skills = [s.strip().lower() for s in applicant_skills.split(',')]
        job_skills = [s.strip().lower() for s in job_skills.split(',')]

        matching = []
        for job_skill in job_skills:
            if any(fuzz.ratio(job_skill, app_skill) > 80 for app_skill in applicant_skills):
                matching.append(job_skill)

        return matching

    def _get_missing_skills(self, applicant_skills, job_skills):
        if not job_skills:
            return []
            
        applicant_skills = [s.strip().lower() for s in applicant_skills.split(',')]
        job_skills = [s.strip().lower() for s in job_skills.split(',')]

        missing = []
        for job_skill in job_skills:
            if not any(fuzz.ratio(job_skill, app_skill) > 80 for app_skill in applicant_skills):
                missing.append(job_skill)

        return missing
