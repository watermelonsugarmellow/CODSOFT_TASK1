import ast
import operator
import random
import re
from datetime import datetime

TOPICS = {
    "array": "An array stores items in contiguous memory, so reading by index is O(1), "
             "but inserting or deleting in the middle is O(n).",
    "linked list": "A linked list is a chain of nodes where each node points to the next. "
                   "Inserting at the head is O(1), but searching is O(n).",
    "stack": "A stack is LIFO (last in, first out). Think of a pile of plates. "
             "Used for undo, recursion and bracket matching.",
    "queue": "A queue is FIFO (first in, first out), like a ticket line. "
             "Used in scheduling and BFS.",
    "tree": "A tree is a hierarchy of nodes. A binary search tree keeps the left child "
            "smaller and the right child larger, giving O(log n) search when balanced.",
    "graph": "A graph is a set of nodes connected by edges. Traverse it with BFS "
             "(level by level) or DFS (deep first).",
    "recursion": "Recursion is when a function calls itself on a smaller problem. "
                 "Always define a base case so it stops.",
    "hash": "A hash map stores key-value pairs and finds a key in O(1) on average by "
            "turning the key into an index with a hash function.",
    "sorting": "Merge sort and quick sort run in O(n log n) on average. Bubble, "
               "selection and insertion sort are O(n^2) and fine only for small inputs.",
    "dynamic programming": "Dynamic programming solves a problem by storing answers to "
                           "overlapping sub-problems so each is computed only once.",
    "big o": "Big-O describes how running time grows with input size: O(1) constant, "
             "O(log n) logarithmic, O(n) linear, O(n^2) quadratic.",
}

QUIZ = [
    ("Which data structure is LIFO?",
     ["a) Queue", "b) Stack", "c) Tree", "d) Graph"], "b"),
    ("Average time to look up a key in a hash map?",
     ["a) O(1)", "b) O(n)", "c) O(log n)", "d) O(n^2)"], "a"),
    ("Which traversal uses a queue?",
     ["a) DFS", "b) Inorder", "c) BFS", "d) Postorder"], "c"),
    ("Which sort has O(n log n) average time?",
     ["a) Bubble sort", "b) Insertion sort", "c) Selection sort", "d) Merge sort"], "d"),
    ("What must every recursive function have?",
     ["a) A loop", "b) A base case", "c) A global variable", "d) A class"], "b"),
]

INTENTS = {
    "greet": ([(r"\b(hi|hello|hey|namaste|hola)\b", 2), (r"good (morning|afternoon|evening)", 2)],
              ["Hey! I'm Prep Buddy. Ask me about interviews, resumes, DSA topics, "
               "or type 'help' to see everything I can do."]),
    "how_are_you": ([(r"\bhow are you\b", 3), (r"\bkaise ho\b", 3), (r"\bwhat'?s up\b", 2)],
                    ["Running at 100% and ready to help you prepare. How's your prep going?"]),
    "identity": ([(r"\bwho are you\b", 3), (r"\byour name\b", 3), (r"\bwhat are you\b", 2)],
                 ["I'm Prep Buddy, a rule-based chatbot that helps students prepare for placements."]),
    "interview": ([(r"\binterview", 2), (r"\b(hr|technical) round\b", 2), (r"\btips?\b", 1)],
                  ["Interview tips: (1) research the company, (2) practise explaining your projects "
                   "out loud, (3) think aloud while solving problems, (4) ask one good question at the end.",
                   "Before an interview, revise your resume line by line - be ready to explain "
                   "everything you wrote on it."]),
    "resume": ([(r"\bresume\b", 3), (r"\bcv\b", 3), (r"\bats\b", 2)],
               ["Resume tips: keep it to one page, put projects with GitHub links near the top, "
                "use action verbs (built, designed, optimised), and add numbers where you can."]),
    "project": ([(r"\bprojects?\b", 2), (r"\bgithub\b", 2), (r"\bportfolio\b", 2)],
                ["Good projects solve a real problem, have a clear README with screenshots, and "
                 "show your commit history. Two solid projects beat ten half-finished ones."]),
    "motivation": ([(r"\b(stressed|nervous|scared|anxious|demotivated|worried|tired)\b", 3),
                    (r"\bgive up\b", 3), (r"\bmotivat", 3), (r"\bfail", 2)],
                   ["Feeling nervous before placements is normal. Take it one small step at a time - "
                    "one topic, one problem, one day. Progress beats perfection.",
                    "Everyone gets rejected sometimes. Each interview is practice for the next one. Keep going!"]),
    "joke": ([(r"\bjoke\b", 3), (r"\bfunny\b", 2), (r"\blaugh\b", 2)],
             ["Why did the developer go broke? Because he used up all his cache.",
              "A SQL query walks into a bar, sees two tables and asks: 'Can I join you?'"]),
    "thanks": ([(r"\b(thanks|thank you|thx|shukriya)\b", 3)],
               ["You're welcome! Keep practising.", "Happy to help!"]),
    "help": ([(r"\bhelp\b", 3), (r"\bwhat can you do\b", 3), (r"\bcommands\b", 2)],
             ["I can: explain topics ('what is a stack'), give interview/resume/project tips, "
              "build a study plan ('study plan'), quiz you ('quiz me'), calculate "
              "('calculate 12*7'), tell the time/date, and remember your name ('my name is ...')."]),
    "bye": ([(r"\b(bye|goodbye|see you|exit|quit)\b", 3)],
            ["Good luck with your prep! Bye!"]),
}

OPS = {ast.Add: operator.add, ast.Sub: operator.sub,
       ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Mod: operator.mod}


def safe_eval(expr):
    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -ev(node.operand)
        raise ValueError("unsupported expression")
    return ev(ast.parse(expr, mode="eval"))

class PrepBuddy:
    def __init__(self):
        self.name = None
        self.state = None          
        self.quiz_index = 0
        self.quiz_score = 0

    def handle_state(self, text):
        if self.state == "ask_hours":
            m = re.search(r"\d+(\.\d+)?", text)
            if not m:
                return "Please tell me a number of hours, for example 3."
            self.state = None
            h = float(m.group())
            if not 0 < h <= 16:
                return "Please pick a realistic number of hours between 1 and 16."
            plan = {"DSA practice": 0.40, "Projects": 0.25,
                    "Aptitude and reasoning": 0.15, "Core CS / revision": 0.20}
            lines = [f"  - {k}: {h * v * 60:.0f} minutes" for k, v in plan.items()]
            return f"Here's a daily plan for {h:g} hour(s):\n" + "\n".join(lines)

        if self.state == "quiz":
            q, options, answer = QUIZ[self.quiz_index]
            choice = re.search(r"\b([abcd])\b", text)
            if not choice:
                return "Please answer with a, b, c or d."
            if choice.group(1) == answer:
                self.quiz_score += 1
                feedback = "Correct!"
            else:
                feedback = f"Not quite. The answer is {answer})."
            self.quiz_index += 1
            if self.quiz_index >= len(QUIZ):
                self.state = None
                return f"{feedback}\nQuiz finished! You scored {self.quiz_score}/{len(QUIZ)}."
            return f"{feedback}\n\n{self.format_question()}"
        return None

    def format_question(self):
        q, options, _ = QUIZ[self.quiz_index]
        return f"Q{self.quiz_index + 1}. {q}\n   " + "\n   ".join(options)

    def get_response(self, user_input):
        text = user_input.lower().strip()
        if not text:
            return "Type something and I'll try to help."

        reply = self.handle_state(text)
        if reply:
            return reply

        m = re.search(r"\b(?:my name is|call me|i am called)\s+([a-z]+)", text)
        if m:
            self.name = m.group(1).capitalize()
            return f"Nice to meet you, {self.name}! Let's get you placement-ready."

        if re.search(r"\bwhat'?s my name\b|\bdo you know my name\b", text):
            return f"You're {self.name}." if self.name else "I don't know yet. Say 'my name is ...'."

        if re.search(r"\bstudy plan\b|\btime ?table\b|\bschedule my study\b", text):
            self.state = "ask_hours"
            return "Sure! How many hours per day can you study?"

        if re.search(r"\bquiz\b|\btest me\b", text):
            self.state, self.quiz_index, self.quiz_score = "quiz", 0, 0
            return "Quiz time! Answer with a, b, c or d.\n\n" + self.format_question()

        m = re.search(r"(?:calculate|compute|solve|what is)\s+([\d\s+\-*/.%()]+)$", text)
        if m:
            try:
                return f"The answer is {safe_eval(m.group(1).strip())}."
            except Exception:
                return "I couldn't work that out. Try something like: calculate 12 * 7"

        if re.search(r"\b(time|samay)\b", text):
            return f"It's {datetime.now().strftime('%I:%M %p')} right now."
        if re.search(r"\b(date|today)\b", text):
            return f"Today is {datetime.now().strftime('%A, %d %B %Y')}."

        for topic, explanation in TOPICS.items():
            if re.search(rf"\b{topic}s?\b", text):
                return explanation

        best_intent, best_score = None, 0
        for intent, (patterns, _) in INTENTS.items():
            score = sum(w for pattern, w in patterns if re.search(pattern, text))
            if score > best_score:
                best_intent, best_score = intent, score
        if best_intent:
            reply = random.choice(INTENTS[best_intent][1])
            if best_intent == "greet" and self.name:
                reply = f"Hey {self.name}! Good to see you again. What shall we work on?"
            return reply

        return random.choice([
            "I didn't get that. Try 'help' to see what I can do.",
            "Hmm, I don't have a rule for that yet. Ask about a topic like 'what is a stack'.",
        ])

    def is_goodbye(self, text):
        return self.state is None and bool(re.search(r"\b(bye|goodbye|exit|quit)\b", text.lower()))


def main():
    bot = PrepBuddy()
    print("Prep Buddy: Hi! I'm Prep Buddy, your placement-prep chatbot. Type 'help' or 'bye'.")
    while True:
        try:
            text = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nPrep Buddy: Bye!")
            break
        print("Prep Buddy:", bot.get_response(text))
        if bot.is_goodbye(text):
            break


if __name__ == "__main__":
    main()