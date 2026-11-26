# Content ideas from the app's code (rork-earnd, commit d26d388, 24 Nov 2026)

Source: Ezy's app repo. These describe what is **built in the code**. Don't claim anything is tested end to end, submitted or live unless Ezy confirms it. Never name the app, show unreleased screens, or give prices.

## Verified in the code
- Hard paywall straight after onboarding, wired to RevenueCat, with monthly and annual plans. No trial.
- The paywall restates the athlete's own plan from onboarding, "so leaving means abandoning their programme rather than skipping an app."
- Onboarding rule in the code: "Every screen either learns something about the athlete or teaches them something about their problem." Answers are applied to the real programme on the last screen.
- The social-proof screen stays hidden until there are real user quotes: "Never invent reviews."
- Progression engine, double progression: "Execution first, reps second, load third." Hold the load until every working set reaches the top of the rep range, and only raise the weight with clean execution. "Never trade range of motion for weight."
- An execution rating is asked once before a session closes, and it gates whether a weight increase is earned.
- An optional acclimation week: practice sessions with one working set each, never auto-increased.
- An "earned moment" screen when every planned set hits the top of the range with clean form, with a shareable story card.
- A Lock Screen Live Activity that updates after every logged set, with Lock Screen buttons.
- A rest timer that stays accurate through backgrounding and relaunch.
- Data export, an exercise library with demo videos, and a progression explainer in plain language.
- App Store screenshot fixtures are compiled only into debug builds and never ship, so demo data stays separate.
- Data is stored locally for now, in a format designed to map onto Firestore later. **Firebase is not integrated yet.**

## Post ideas (Dan Koe style: sentence case, one idea, from real work)

1. **Execution first** (idea): "My app won't let you add weight just because you hit the reps. Execution first, reps second, load third. Most training apps reward the number. I wanted one that rewards the rep."
2. **Never invent reviews** (integrity): The onboarding has a social-proof screen that stays hidden until real users have said something. "Fake reviews are the easiest screen to build and the most expensive one to ship."
3. **The paywall restates your plan** (product lesson): "A paywall shouldn't sell the app. It should show the person the plan they just built, so leaving means abandoning their programme, not skipping a download."
4. **Every onboarding screen earns its place**: "Every screen either learns something about the user or teaches them something about their problem. If it does neither, it's friction."
5. **Practice week** (decision): "The first week in my app is practice. One set per exercise, weights carried forward as suggestions, nothing auto-increased. People quit programmes that start too heavy."
6. **The earned moment** (build-in-public): "I built one screen to feel loud: when every set hits the top of the range with clean form. It's the only time the app celebrates."
7. **Lock Screen** (build detail): the Live Activity updates after every set, so the phone can stay in your pocket between sets. Pair it with a short screen recording only once Ezy is happy to show UI.
8. **Screenshots that never ship** (process): App Store screenshot data is compiled only into debug builds. "Demo data should be impossible to ship by accident."
9. **What's left** (honest update): RevenueCat is wired in, Firebase isn't yet. "The paywall exists. The thing that remembers who you are across phones doesn't."
10. **Article idea**: "The rules my app enforces so I can't lie to users", covering execution-gated progression, no invented reviews, no trial, labelled demo data and no physique promises.
11. **Thread idea**: "Double progression, explained by the code that enforces it", in 5 posts, with no app name.
12. **Contrarian**: "Most fitness apps add weight when you hit the number. That's how you end up trading range of motion for load."

## Check before posting
- Idea 5: the code describes acclimation as optional. Present it as optional.
- Idea 12: frame it as an opinion ("a lot of apps"), not a universal claim.
- Don't use the code's 12-week strength projection in content. It conflicts with the no-promises rules.
