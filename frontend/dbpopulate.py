import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'filquiz.settings'
django.setup()

#python3 dbpopulate.py filename domain category

import csv, random, sys
from game.models import Question, Choice, Category, Domain
filename = sys.argv[1]
d,res = Domain.objects.get_or_create(domain=sys.argv[2])
d.save()
cat, res = Category.objects.get_or_create(category=sys.argv[3],domain=d)
cat.save()

with open('Questions-Repo/'+filename) as f:
    questions = csv.reader(f)
    for question in questions:
        text = question[0]
        c = Choice(choice=question[1],correct=True)
        c.save()
        choice_list = [c]
        for choice in question[2:]:
            if not choice:
                break
            c = Choice(choice=choice)
            c.save()
            choice_list.append(c)

        random.shuffle(choice_list)
        q = Question(question=text,category=cat)
        q.save()
        q.choices.set(choice_list)
        q.save()
