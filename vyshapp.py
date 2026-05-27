#!/usr/bin/env python3
"""
LinkedIn Post Generator — vyshapp.py
Run: python vyshapp.py
"""

from __future__ import annotations

import argparse
import random
import textwrap
from dataclasses import dataclass


@dataclass(frozen=True)
class PostRequest:
    topic: str
    bullets: list[str]
    tone: str
    length: str
    include_hashtags: bool
    cta_style: str


HOOKS: dict[str, list[str]] = {
    "professional": [
        "A quick observation on {topic}:",
        "Three things I learned about {topic}:",
        "If you're working on {topic}, this might help.",
    ],
    "casual": [
        "Real talk about {topic}.",
        "Nobody warned me about {topic}.",
        "Hot take on {topic} (hear me out):",
    ],
    "story": [
        "Last week, {topic} taught me something I didn't expect.",
        "I used to get {topic} completely wrong.",
        "Here's a short story about {topic}.",
    ],
    "bold": [
        "Stop ignoring {topic}.",
        "Unpopular opinion: most advice on {topic} is outdated.",
        "{topic} is not optional anymore.",
    ],
}

CLOSINGS: dict[str, list[str]] = {
    "question": [
        "What's your experience with {topic}?",
        "How are you approaching {topic} this quarter?",
        "What would you add to this list?",
    ],
    "invite": [
        "Drop your thoughts in the comments — I read every one.",
        "Share this with someone who needs it.",
        "Follow for more on {topic}.",
    ],
    "soft": [
        "Hope this saves you some time.",
        "Worth a bookmark if you're building in this space.",
    ],
}

HASHTAG_POOL = [
    "LinkedIn",
    "CareerGrowth",
    "Leadership",
    "PersonalBranding",
    "Productivity",
    "Learning",
    "BuildInPublic",
    "Startup",
    "Hiring",
    "Tech",
]


def _pick(pool: list[str], topic: str) -> str:
    return random.choice(pool).format(topic=topic)


def _format_bullets(bullets: list[str], style: str) -> str:
    if not bullets:
        return ""
    if style == "arrows":
        return "\n".join(f"- {b.strip()}" for b in bullets if b.strip())
    if style == "numbers":
        lines = [b.strip() for b in bullets if b.strip()]
        return "\n".join(f"{i}. {line}" for i, line in enumerate(lines, 1))
    return "\n".join(f"* {b.strip()}" for b in bullets if b.strip())


def _body_paragraphs(req: PostRequest) -> list[str]:
    topic = req.topic.strip()
    bullets = [b for b in req.bullets if b.strip()]

    if req.tone == "story":
        parts = [
            f"I kept running into the same wall with {topic}.",
            "So I changed one habit and tracked the result for two weeks.",
        ]
        if bullets:
            parts.append("What actually moved the needle:")
        return parts

    if req.tone == "casual":
        parts = [f"Most people overcomplicate {topic}."]
        if bullets:
            parts.append("Here's the simpler version:")
        else:
            parts.append("Start small, stay consistent, iterate weekly.")
        return parts

    if req.tone == "bold":
        parts = [
            f"If {topic} isn't on your roadmap, you're already behind.",
            "The winners aren't smarter — they're faster at testing.",
        ]
        if bullets:
            parts.append("Focus here first:")
        return parts

    # professional (default)
    parts = [
        f"I've been deep in {topic} lately, and a few patterns keep showing up.",
    ]
    if bullets:
        parts.append("Key takeaways:")
    else:
        parts.append("Clarity beats complexity every time.")
    return parts


def _hashtag_line(topic: str, count: int = 4) -> str:
    words = [w for w in topic.replace("-", " ").split() if len(w) > 2]
    custom = ["".join(w[:1].upper() + w[1:] for w in topic.split()[:2])] if topic else []
    tags = []
    for tag in custom + random.sample(HASHTAG_POOL, k=min(count, len(HASHTAG_POOL))):
        clean = "".join(ch for ch in tag if ch.isalnum())
        if clean and clean not in tags:
            tags.append(clean)
    return " ".join(f"#{t}" for t in tags[:count])


def generate_post(req: PostRequest) -> str:
    topic = req.topic.strip() or "your work"
    hooks = HOOKS.get(req.tone, HOOKS["professional"])
    closings = CLOSINGS.get(req.cta_style, CLOSINGS["question"])

    hook = _pick(hooks, topic)
    body_parts = _body_paragraphs(req)
    bullet_block = _format_bullets(
        req.bullets,
        style="arrows" if req.tone in ("professional", "bold") else "numbers",
    )
    closing = _pick(closings, topic)

    sections: list[str] = [hook, ""]
    sections.extend(body_parts)
    if bullet_block:
        sections.extend(["", bullet_block])
    sections.extend(["", closing])

    if req.length == "long":
        sections.insert(
            2,
            textwrap.fill(
                f"Whether you're leading a team or learning solo, {topic} rewards "
                "people who ship, measure, and share what they learn.",
                width=72,
            ),
        )

    post = "\n".join(sections).strip()
    post = "\n\n".join(block.strip() for block in post.split("\n\n") if block.strip())

    if req.include_hashtags:
        post += "\n\n" + _hashtag_line(topic)

    return post


def interactive() -> PostRequest:
    print("\n=== LinkedIn Post Generator (vyshapp) ===\n")
    topic = input("Topic (e.g. AI productivity, new job, side project): ").strip()
    print("Bullet points (blank line to finish):")
    bullets: list[str] = []
    while True:
        line = input("  - ").strip()
        if not line:
            break
        bullets.append(line)

    print("\nTone: 1=professional  2=casual  3=story  4=bold")
    tone_map = {"1": "professional", "2": "casual", "3": "story", "4": "bold"}
    tone_choice = input("Choose [1]: ").strip() or "1"
    tone = tone_map.get(tone_choice, "professional")

    print("\nLength: 1=short  2=long")
    length = "long" if input("Choose [1]: ").strip() == "2" else "short"

    print("\nClosing: 1=question  2=invite  3=soft")
    cta_map = {"1": "question", "2": "invite", "3": "soft"}
    cta_choice = input("Choose [1]: ").strip() or "1"
    cta_style = cta_map.get(cta_choice, "question")

    hashtags = input("\nAdd hashtags? [Y/n]: ").strip().lower() not in ("n", "no")

    return PostRequest(
        topic=topic,
        bullets=bullets,
        tone=tone,
        length=length,
        include_hashtags=hashtags,
        cta_style=cta_style,
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="LinkedIn Post Generator")
    p.add_argument("--topic", "-t", help="Post topic")
    p.add_argument("--bullet", "-b", action="append", default=[], help="Bullet point (repeatable)")
    p.add_argument(
        "--tone",
        choices=["professional", "casual", "story", "bold"],
        default="professional",
    )
    p.add_argument("--length", choices=["short", "long"], default="short")
    p.add_argument(
        "--cta",
        choices=["question", "invite", "soft"],
        default="question",
        help="Closing style",
    )
    p.add_argument("--no-hashtags", action="store_true")
    p.add_argument("-o", "--output", help="Save post to file")
    p.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    p.add_argument("--seed", type=int, help="Random seed for reproducible output")
    return p


def _running_under_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except ImportError:
        return False


def run_streamlit_ui() -> None:
    import streamlit as st

    st.set_page_config(
        page_title="LinkedIn Post Generator",
        page_icon="💼",
        layout="centered",
    )
    st.title("LinkedIn Post Generator")
    st.caption("Powered by vyshapp.py")

    with st.sidebar:
        st.header("Settings")
        tone = st.selectbox(
            "Tone",
            ["professional", "casual", "story", "bold"],
            index=0,
        )
        length = st.radio("Length", ["short", "long"], horizontal=True)
        cta_style = st.selectbox(
            "Closing style",
            ["question", "invite", "soft"],
            format_func=lambda x: x.capitalize(),
        )
        include_hashtags = st.checkbox("Add hashtags", value=True)
        seed = st.number_input(
            "Random seed (optional)",
            min_value=0,
            value=0,
            step=1,
            help="Set to 0 to randomize each time.",
        )

    topic = st.text_input(
        "Topic",
        placeholder="e.g. AI productivity, new job, side project",
    )
    bullets_text = st.text_area(
        "Bullet points (one per line)",
        placeholder="Use templates\nEdit in your voice\nShip weekly",
        height=120,
    )

    col1, col2 = st.columns(2)
    with col1:
        generate = st.button("Generate post", type="primary", use_container_width=True)
    with col2:
        regenerate = st.button("Regenerate", use_container_width=True)

    if generate or regenerate:
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            if seed > 0:
                random.seed(int(seed))
            bullets = [line.strip() for line in bullets_text.splitlines() if line.strip()]
            req = PostRequest(
                topic=topic.strip(),
                bullets=bullets,
                tone=tone,
                length=length,
                include_hashtags=include_hashtags,
                cta_style=cta_style,
            )
            post = generate_post(req)
            st.session_state["last_post"] = post

    if "last_post" in st.session_state:
        st.subheader("Your post")
        st.text_area(
            "Copy and paste to LinkedIn",
            st.session_state["last_post"],
            height=320,
            label_visibility="collapsed",
        )
        st.download_button(
            "Download .txt",
            st.session_state["last_post"],
            file_name="linkedin_post.txt",
            mime="text/plain",
            use_container_width=True,
        )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    if args.interactive or not args.topic:
        req = interactive()
    else:
        req = PostRequest(
            topic=args.topic,
            bullets=args.bullet or [],
            tone=args.tone,
            length=args.length,
            include_hashtags=not args.no_hashtags,
            cta_style=args.cta,
        )

    post = generate_post(req)
    print("\n" + "=" * 50)
    print(post)
    print("=" * 50 + "\n")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(post + "\n")
        print(f"Saved to {args.output}")


if _running_under_streamlit():
    run_streamlit_ui()
elif __name__ == "__main__":
    main()
