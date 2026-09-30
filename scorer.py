


def judge(question, expects, answer, results):
    """
    Return True when the generated answer contains the expected phrase.

    This is intentionally simple and deterministic. The expected phrase
    was defined before running the evaluation in questions.py.
    """

    if not answer:
        return False

    if not expects:
        return False

    answer_text = " ".join(answer.lower().split())
    expected_text = " ".join(expects.lower().split())

    return expected_text in answer_text