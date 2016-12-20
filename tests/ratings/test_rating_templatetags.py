import json
import pytest
import re

from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType

from tests import helpers

def react_ratings_render_for_props(rf, user, question):
    request = rf.get('/')
    request.user = user
    template = '{% load react_ratings %}{% react_ratings question %}'
    context = {'request': request, "question": question}

    # normally annotated by queryset
    question.negative_rating_count = 0
    question.positive_rating_count = 0

    content_type = ContentType.objects.get_for_model(question)
    expected = (
        r'^<div id=\"ratings_for_{ct}_{pk}\"><\/div><script>window\.opin\.renderRatings\('
        r'\"ratings_for_{ct}_{pk}\", (?P<props>{{.+}})\)<\/script>$'
    ).format(ct=content_type.id, pk=question.id)

    match = re.match(expected, helpers.render_template(template, context))
    assert match
    assert match.group('props')
    props = json.loads(match.group('props'))
    assert props['contentType'] == content_type.id
    assert props['objectId'] == question.id
    del props['contentType']
    del props['objectId']
    return props


@pytest.mark.django_db
def test_react_rating_anonymous(rf, question):
    user = AnonymousUser()
    props = react_ratings_render_for_props(rf, user, question)

    assert props == {
        'authenticatedAs': None,
        'isReadOnly': True,
        'negativeRatings': 0,
        'positiveRatings': 0,
        'style': 'ideas',
        'userRating': None,
        'userRatingId': -1
    }


@pytest.mark.django_db
def test_react_rating_user(rf, user, question, rating):
    props = react_ratings_render_for_props(rf, user, question)

    assert props == {
        'authenticatedAs': user.username,
        'isReadOnly': True,
        'negativeRatings': 0,
        'positiveRatings': 0,
        'style': 'ideas',
        'userRating': rating.value,
        'userRatingId': rating.id,
    }

