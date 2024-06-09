from sector_assessment.models import Result


def create_result(user, assessment_run_object, question_attempts):
    sectors = {}
    skills = {}
    for question_attempt in question_attempts:
        choice = question_attempt.choice
        for skill in choice.skills.all():
            skills.setdefault(skill.name, 0)
            skills[skill.name] += 1
            for sector in skill.sectors.all():
                sectors.setdefault(sector.name, 0)
                sectors[sector.name] += 1
    result_data = {
        "user": user,
        "skill_score": skills,
        "sector_score": sectors,
        "assessment_run": assessment_run_object
    }

    # Create and save the Result object
    result = Result.objects.create(
        user=result_data["user"],
        skill_score=result_data["skill_score"],
        sector_score=result_data["sector_score"],
        assessment_run=result_data["assessment_run"]
    )

    return result
