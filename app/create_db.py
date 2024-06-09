import os
import django
from django.contrib.auth import get_user_model

# Ensure the settings module is set
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Setup Django so that apps are ready
django.setup()


from core.models import Sector, Skill  # noqa: E402
from sector_assessment.models import Choice, Question, Assessment  # noqa: E402

user = get_user_model()


def create_super_user():
    user.objects.create_user(
        email="admin@admin.com",
        password="akhu1234",
        name='Akhu',
        is_staff=True,
        is_superuser=True
    )
    return


def create_staff():
    user.objects.create(
        email='staff1@example.com',
        password='text31234',
        name='Staff 1'
    )
    user.objects.create(
        email='staff2@example.com',
        password='text21234',
        name='Staff 2'
    )
    user.objects.create(
        email='staff3@example.com',
        password='text11234',
        name='Staff 3'
    )


def create_user():
    user.objects.create(
        email='user1@example.com',
        password='text31234',
        name='User 1'
    )
    user.objects.create(
        email='user2@example.com',
        password='text21234',
        name='User 2'
    )
    user.objects.create(
        email='user3@example.com',
        password='text11234',
        name='User 3'
    )


def create_sector():
    Sector.objects.create(id=1, name='Sample Sector 1')
    Sector.objects.create(id=2, name='Sample Sector 2')
    Sector.objects.create(id=3, name='Sample Sector 3')


def create_skill():
    sectors = Sector.objects.all()
    skill1 = Skill.objects.create(id=1, name='Sample Skill 1')
    skill2 = Skill.objects.create(id=2, name='Sample Skill 2')
    skill3 = Skill.objects.create(id=3, name='Sample Skill 3')
    skill1.sectors.set([sectors[1], sectors[2]])
    skill2.sectors.set([sectors[0]])
    skill3.sectors.set([sectors[2], sectors[0]])


def create_question():
    Question.objects.create(id=1, title='Sample Question 1')
    Question.objects.create(id=2, title='Sample Question 2')


def create_choice():
    skills = Skill.objects.all()
    questions = Question.objects.all()
    for i in range(8):
        choice = Choice.objects.create(
            id=i+1,
            choice_text="This is choice {}".format(i+1),
            question=questions[i//4])
        choice.skills.set(
            [skills[i % skills.count()], skills[(i+1) % skills.count()]])


def create_assessment():
    questions = Question.objects.all()
    users = user.objects.all()
    assessment = Assessment.objects.create(id=1, title='Sample Assessment 1')
    assessment.questions.set(questions)
    assessment.allowed_users.set(users)


if __name__ == "__main__":
    create_super_user()
    create_staff()
    create_user()
    create_sector()
    create_skill()
    create_question()
    create_choice()
    create_assessment()
