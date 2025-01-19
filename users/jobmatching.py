from dataclasses import dataclass
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from fuzzywuzzy import fuzz
import json

@dataclass
class StudentProfile:
    name: str
    skills: List[str]
    experience: float
    education: str
    description: str

@dataclass
class JobPosting:
    title: str
    required_skills: List[str]
    required_experience: float
    required_education: str
    description: str

class AdvancedJobMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        
    def calculate_match(self, student, job):
        weights = {
            'skills_match': 0.35,
            'experience_match': 0.25,
            'education_match': 0.20,
            'description_match': 0.20
        }
        
        scores = {
            'skills_match': self._calculate_skills_score(student.skills, job.required_skills),
            'experience_match': self._calculate_experience_score(student.experience, job.required_experience),
            'education_match': self._calculate_education_score(student.education, job.required_education),
            'description_match': self._calculate_description_similarity(student.description, job.description)
        }
        
        final_score = sum(scores[k] * weights[k] for k in weights)
        return final_score, scores
    
    def _calculate_skills_score(self, student_skills, job_skills):
        student_skills = set(s.lower().strip() for s in student_skills)
        job_skills = {s.lower().strip(): i for i, s in enumerate(job_skills, 1)}
        
        max_score = sum(range(1, len(job_skills) + 1))
        current_score = 0
        
        for job_skill, importance in job_skills.items():
            best_match = max(
                fuzz.ratio(job_skill, student_skill) 
                for student_skill in student_skills
            )
            if best_match > 80:
                current_score += importance
                
        return (current_score / max_score) * 100 if max_score > 0 else 0
    
    def _calculate_experience_score(self, student_exp, required_exp):
        if student_exp >= required_exp:
            if student_exp <= required_exp * 1.5:
                return 100
            else:
                return 100 * (required_exp * 1.5) / student_exp
        else:
            return (student_exp / required_exp) * 100
    
    def _calculate_education_score(self, student_edu, required_edu):
        education_levels = {
            'high school': 1,
            'bachelor': 2,
            'master': 3,
            'phd': 4
        }
        
        student_level = education_levels.get(student_edu.lower(), 0)
        required_level = education_levels.get(required_edu.lower(), 0)
        
        if student_level >= required_level:
            return 100
        else:
            return (student_level / required_level) * 100
    
    def _calculate_description_similarity(self, student_desc, job_desc):
        texts = [student_desc, job_desc]
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        similarity = (tfidf_matrix * tfidf_matrix.T).toarray()[0][1]
        return similarity * 100

    def get_matching_skills(self, student_skills, job_skills):
        matching = []
        for job_skill in job_skills:
            for student_skill in student_skills:
                if fuzz.ratio(job_skill.lower(), student_skill.lower()) > 80:
                    matching.append(job_skill)
                    break
        return matching

    def get_missing_skills(self, student_skills, job_skills):
        missing = []
        for job_skill in job_skills:
            matched = False
            for student_skill in student_skills:
                if fuzz.ratio(job_skill.lower(), student_skill.lower()) > 80:
                    matched = True
                    break
            if not matched:
                missing.append(job_skill)
        return missing

    def get_match_details(self, student, job):
        score, component_scores = self.calculate_match(student, job)
        
        return {
            'student_name': student.name,
            'job_title': job.title,
            'overall_match': round(score, 2),
            'component_scores': {k: round(v, 2) for k, v in component_scores.items()},
            'matching_skills': self.get_matching_skills(student.skills, job.required_skills),
            'missing_skills': self.get_missing_skills(student.skills, job.required_skills)
        }

# Example usage with multiple students and a job
def main():
    # Create a job posting
    job = JobPosting(
        title="Senior Full Stack Developer",
        required_skills=["Python", "Django", "React", "AWS", "PostgreSQL", "Docker"],
        required_experience=5,
        required_education="bachelor",
        description="Looking for a senior full stack developer with strong Python and JavaScript skills. Must have experience with Django, React, and cloud services. Should be able to lead technical projects and mentor junior developers."
    )

    # Create multiple student profiles
    students = [
        StudentProfile(
            name="Alice Johnson",
            skills=["Python", "Django", "React", "MySQL", "Docker"],
            experience=6,
            education="master",
            description="Senior developer with 6 years of experience in full stack development. Proficient in Python, Django, and React. Led multiple technical projects and mentored junior developers."
        ),
        StudentProfile(
            name="Bob Smith",
            skills=["Python", "Flask", "Angular", "AWS", "MongoDB"],
            experience=4,
            education="bachelor",
            description="Full stack developer with 4 years of experience. Specialized in Python and Angular development. Experience with AWS and MongoDB."
        ),
        StudentProfile(
            name="Carol Davis",
            skills=["Java", "Spring", "React", "Oracle", "Kubernetes"],
            experience=7,
            education="bachelor",
            description="Senior Java developer transitioning to full stack development. Strong experience in enterprise applications and cloud infrastructure."
        )
    ]

    # Match all students against the job
    matcher = AdvancedJobMatcher()
    results = []
    
    for student in students:
        match_details = matcher.get_match_details(student, job)
        results.append(match_details)
    
    # Sort results by overall match score
    results.sort(key=lambda x: x['overall_match'], reverse=True)
    
    # Print results in a formatted way
    print("\nJob Matching Results")
    print("=" * 50)
    print(f"Position: {job.title}\n")
    
    for rank, result in enumerate(results, 1):
        print(f"Rank {rank}: {result['student_name']}")
        print(f"Overall Match: {result['overall_match']}%")
        print("\nComponent Scores:")
        for component, score in result['component_scores'].items():
            print(f"- {component}: {score}%")
        print("\nMatching Skills:", ", ".join(result['matching_skills']))
        print("Missing Skills:", ", ".join(result['missing_skills']))
        print("-" * 50)

if __name__ == "__main__":
    main()