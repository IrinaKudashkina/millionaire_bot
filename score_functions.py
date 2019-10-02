score = {}


def victories(user, scores):
    if user in score:
        score[user]['victories'] += scores
    else:
        score[user] = {'victories': 0, 'defeats': 0}
        score[user]['victories'] += scores


def defeats(user, scores):
    if user in score:
        score[user]['defeats'] += scores
    else:
        score[user] = {'victories': 0, 'defeats': 0}
        score[user]['defeats'] += scores
