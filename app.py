from flask import Flask, render_template, request
import random

app = Flask(__name__)

# Data
FALLACY_PHRASES = [
    "Coincidence? I think not.",
    "They don't want you to know the truth.",
    "Follow the money — it's always the money.",
    "This explains everything they hid from us.",
    "There’s more behind this than meets the eye.",
    "Ask yourself who benefits."
]

VILLAINS = ["The Aurora Order", "The Meridian Council", "The Helix Corporation", "The Obsidian Trust"]
LOCATIONS = ["Aurora County", "Ridgehaven", "New Meridian", "Obsidian Bay"]

BLOCKED_WORDS = {"kill", "bomb", "attack", "assassinate", "poison", "explode", "shoot", "stab"}

BASE_TEMPLATES = [
    "In {location}, recent events suggest a coordinated effort by {villain}.",
    "Residents whisper that {villain} has been operating in secret.",
    "Official explanations don’t add up; subtle clues keep pointing to {villain}.",
    "Unusual coincidences seem to circle back to {villain}."
]

EMOTION_TAG = {
    "Neutral": "notable",
    "Concerned": "concerning",
    "Fearful": "alarming",
    "Angry": "infuriating"
}

def build_narrative(villain, location, emotion, fallacy_density, implausibility):
    # shuffle sentence templates and pick 3–4
    sents = BASE_TEMPLATES.copy()
    random.shuffle(sents)
    text = " ".join(sents[:random.choice([3, 4])])

    # sprinkle fallacy phrases
    n_fallacies = max(0, min(10, fallacy_density))
    if n_fallacies:
        text += " " + " ".join(random.choice(FALLACY_PHRASES) for _ in range(n_fallacies))

    # add emotional qualifier
    emo_word = EMOTION_TAG.get(emotion, "notable")
    text += f" This is {emo_word}."

    # implausibility add-on
    try:
        impl = float(implausibility)
    except:
        impl = 0.0
    if impl >= 0.7:
        text += " Claims escalate into improbable chains of causality that strain plausibility."

    # personalize
    text = text.format(location=location, villain=villain)
    return text

def violates_policy(txt: str) -> bool:
    low = txt.lower()
    return any(b in low for b in BLOCKED_WORDS)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/simulator", methods=["GET", "POST"])
def simulator():
    result = None
    villain = VILLAINS[0]
    location = LOCATIONS[0]
    emotion = "Neutral"
    fallacy_density = 2
    implausibility = 0.3

    if request.method == "POST":
        villain = request.form.get("villain", villain)
        location = request.form.get("location", location)
        emotion = request.form.get("emotion", emotion)
        fallacy_density = int(request.form.get("fallacy", fallacy_density))
        implausibility = float(request.form.get("implausibility", implausibility))

        text = build_narrative(villain, location, emotion, fallacy_density, implausibility)

        # Safety
        if violates_policy(text):
            result = "[REDACTED DUE TO SAFETY]"
        else:
            result = "=== FAKE / FOR RESEARCH & EDUCATION ONLY ===\n\n" + text

    return render_template(
        "simulator.html",
        villains=VILLAINS,
        locations=LOCATIONS,
        result=result,
        preset={"villain": villain, "location": location, "emotion": emotion,
                "fallacy": fallacy_density, "implausibility": implausibility}
    )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/safety")
def safety():
    return render_template("safety.html")

if __name__ == "__main__":
    app.run(debug=True)
