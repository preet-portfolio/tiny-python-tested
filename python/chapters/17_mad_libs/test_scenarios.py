"""Real-world cases for mad.py: a template engine meets real answers.

Email and notification templates ("Hi <first name>, your <item> has shipped") are Mad Libs
with real users. They type backslashes, the template has brackets that aren't blanks, and
sometimes a value is missing. A half-filled email must never go out.
"""

import os
from subprocess import getstatusoutput

prg = "./mad.py"


def story(template: str, answers: str) -> tuple[int, str]:
    name = "scenario-story.txt"
    with open(name, "w", encoding="utf-8") as fh:
        fh.write(template)
    try:
        return getstatusoutput(f"{prg} {name} -i {answers}")
    finally:
        os.remove(name)


def test_backslashes_are_kept():
    """an answer like C:\\new\\docs goes in exactly as typed"""
    rv, out = story("Saved to <folder>.", r"'C:\new\docs'")
    assert rv == 0
    assert out == r"Saved to C:\new\docs."


def test_odd_blank_names_work():
    """a blank called <noun (plural)> or <verb+ing> still gets filled"""
    rv, out = story("Two <noun (plural)> were <verb+ing>.", "cats dancing")
    assert rv == 0
    assert out == "Two cats were dancing."


def test_maths_is_not_a_blank():
    """'5 < 6 and 7 > 3' is maths: only <animal> is a blank"""
    rv, out = story("I know 5 < 6 and 7 > 3, said the <animal>.", "owl")
    assert rv == 0
    assert out == "I know 5 < 6 and 7 > 3, said the owl."


def test_too_few_answers_is_an_error():
    """three blanks and two answers: stop with a clear message, no half-told story"""
    rv, out = story("<a> <b> <c>", "one two")
    assert rv != 0
    assert "3 blanks" in out and "2 answers" in out
    assert "Traceback" not in out


def test_too_many_answers_is_an_error():
    """two blanks and three answers: say so instead of dropping one"""
    rv, out = story("<a> and <b>", "one two three")
    assert rv != 0
    assert "2 blanks" in out and "3 answers" in out


def test_same_blank_twice_gets_two_answers():
    """<noun> twice asks twice, filled in order"""
    rv, out = story("A <noun> met a <noun>.", "frog prince")
    assert rv == 0
    assert out == "A frog met a prince."


def test_story_from_stdin():
    """'-' means read the story from the keyboard (STDIN)"""
    rv, out = getstatusoutput(f"{prg} - -i blue < inputs/no_blanks.txt")
    assert rv != 0
    assert "has no placeholders" in out


def test_asks_at_the_keyboard():
    """with no -i, it asks for each blank, with the right a/an"""
    # (the answers file is left behind so the same command can be run again by hand)
    with open("answers-full.txt", "w", encoding="utf-8") as fh:
        fh.write("surly\ncar\nunder\nbicycle\n")
    rv, out = getstatusoutput(f"{prg} inputs/fox.txt < answers-full.txt")
    assert rv == 0
    assert "Give me an adjective: " in out and "Give me a noun: " in out
    assert out.endswith("The quick surly car jumps under the lazy bicycle.")


def test_running_out_of_answers_at_the_keyboard():
    """if the keyboard input ends early, it says which word is missing, no crash"""
    # (the answers file is left behind so the same command can be run again by hand)
    with open("answers-short.txt", "w", encoding="utf-8") as fh:
        fh.write("surly\n")
    rv, out = getstatusoutput(f"{prg} inputs/fox.txt < answers-short.txt")
    assert rv != 0
    assert "still needed a noun" in out
    assert "Traceback" not in out
