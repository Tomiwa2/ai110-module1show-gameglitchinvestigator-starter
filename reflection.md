# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
    Ans: 
    - When I first loaded the game, the visual layout looked perfectly normal and nothing seemed out of place.
      However, the first time I tried to actually play, I immediately ran into a functional bug. 
      The text input box explicitly told me to 'Press Enter to apply' my guess, but pressing Enter did absolutely nothing. 
      I had to figure out that the Enter key was broken and I actually needed to manually click the 'Submit Guess' button
      for the game to register my number!"

- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
  Ans: 
  1. **Expected**: When a new game starts with an "Attempts allowed" setting of 8, the "Attempts left" counter should also start at exactly 8 ans they should match over the course of the game
     **Actual**: The game starts at 7 attempts left before any guess is even made.

  2. **Expected**: When a guess is lower than the secret number, the game should display a hint telling the user to guess higher.
     **Actual**: The hint logic is completely reversed; if the secret number is higher, the game incorrectly says to go lower (and vice versa).

  3. **Expected**: Clicking the "New Game" button should reset the board and scores, and restore the attempts counter without needing to reload the webpage.
     **Actual**: The "New Game" button does not restart the game neither does winning; a full browser refresh is required to actually start over.

  4. **Expected**: The game should correctly tally and update the player's score at the end of a round across all difficulty settings.
     **Actual**: Scores are failing to tally correctly/not showing when playing in Normal and Easy difficulty modes.

  5. **Expected**: Changing the difficulty in the middle of a game should either completely reset the game state or gracefully apply the new rules to the next round.
     **Actual**: Changing the difficulty mid-game randomly alters the attempt limit but keeps the current score state exactly the same.

  6. **Expected**: If a user enters a guess outside the specified 1 to 100 range (like a negative number or something over 100), the game should reject it and display an error message or prompt.
    **Actual**: Absolutely nothing happens when guessing outside the allowed range; the game fails silently.

  7. **Expected**: "Easy" mode should provide the player with a higher number of allowed attempts compared to "Normal" mode to actually make the game easier.
     **Actual**: "Easy" mode assigns fewer attempts than "Normal" mode, unintentionally making it harder.

    
**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.


| Input                     | Expected Behavior n| Actual Behavior        | Console Output / Error |
|---------------------------|--------------------|------------------------|------------------------|
|Guess of 8 vs secret of 19 | Go lower hint      | Go higer hint showed   | none                   |
|Select "Easy" as           | More attempts than | Game assigns fewer     | none                   |
 difficulty                  "Normal" diificulty|  attempts than "Normal",
                                                   making it harder.
|Enter "150" (or no         | Game should reject | Nothing               | none                   |
 outside 1-100) and click     input and show 
 Submit                       "out of bounds" error            
|Range in setting !=        | They should match | They so not            | none
  range on page for each
  difficulty
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
Ans: Claude and Gemini

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
Ans: for the backwards hint, AI suggested that the correct fix should be
   if guess > secret:
      return "Too High", "📉 Go LOWER!"   # too high → aim lower
   else:
      return "Too Low", "📈 Go HIGHER!"   # too low → aim higher

   I first verified this by mentally tracing the logic (if secret is 10 and guess is 20, 20 > 10, so "Too High, Go lower" is the correct output). I then applied the suggested code fix to the application, refreshed the game, and intentionally guessed higher and lower than the secret number to confirm the hints were finally displaying accurately!

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
Ans: When I asked an AI how to fix the bug where the game starts with 7 attempts instead of 8, it gave me a misleading suggestion.

The AI suggested that I should just change the initial code to say attempts_allowed = 9. It explained that since the game is accidentally subtracting 1 when the page loads, starting it at 9 would make it visually display 8 to the user, "fixing" the problem.

While this would technically make the screen show the number 8, I verified through logical reasoning that this is a bad, misleading practice. It doesn't actually solve the underlying problem; the fact that the game logic is running a subtraction function at the wrong time. If another developer came along later and fixed the underlying load sequence, the game would suddenly start giving players 9 attempts! A true fix requires stopping the subtraction from happening before a guess is made, not just changing the starting number.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
   Ans: I decided a bug was really fixed only when I could confirm it two ways: by reproducing the original broken behavior, then watching that exact scenario behave correctly after the change. For the reversed hint bug, that meant deliberately guessing both above and below the secret number and checking the hint pointed the right way each time. I didn't trust a fix just because the screen "looked right" once: I wanted a repeatable test that would catch the bug again if it ever came back. A fix that only changed the displayed result without addressing the underlying logic (like setting attempts to 9 to mask a subtraction bug) didn't count as fixed to me.

- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
   Ans: I wrote pytest tests in tests/test_game_logic.py and ran them with python -m pytest, ending with 7 passing tests. The most useful one was test_too_high_tells_player_to_go_lower, which calls check_guess(60, 50) and asserts the outcome is "Too High" AND that the message contains "LOWER" but not "HIGHER". This showed me my hint fix worked for the normal case, and it also exposed something I hadn't noticed: the app sometimes passes the secret number as a string, so I added test_hint_direction_with_string_secret_too_high to confirm the fix held in that fallback branch too. I also had to repair the pre-existing tests, which were broken because they compared the (outcome, message) tuple against a plain string instead of unpacking it.

- Did AI help you design or understand any tests? How?
   Ans: Yes — I used Claude Code in agent mode to help author the regression tests and to repair the broken pre-existing ones. The most helpful part was AI pointing out edge cases I would have missed on my own, like the fact that check_guess can receive the secret as a string and hit a TypeError fallback path, which needed its own test. AI also helped me understand why the old tests were failing; that asserting a string against a returned tuple will never match rather than just handing me a fix. I still verified each test by running pytest myself and tracing the logic, so I understood what each assertion was actually proving.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
   Ans: I'd tell my friend that Streamlit isn't like a normal program that runs once and then waits for you. Instead, every single time you interact with the page; typing in a box, clicking a button, or changing the difficulty dropdown, Streamlit re-runs your entire script from the top all over again. That "rerun" behavior is exactly why our game's secret number kept changing on every guess at first: the line that picked a random number was running fresh on every click, so it never had a chance to stay the same. Session state (st.session_state) is the fix for that, it's like a small backpack that survives the rerun, so anything you store in it (the secret number, the score, the attempt count) is remembered instead of being rebuilt from scratch. The key pattern we used was "only set it if it doesn't already exist" (if "secret" not in st.session_state:), which creates the value once and then lets it persist across all the reruns that follow.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
  Ans: Better and more detailed prompting. It was not only easy on me but on the agent. 
 
- What is one thing you would do differently next time you work with AI on a coding task?
Letting the agent do the heavy lifting of translating my ideas and just verifying was what I wanted; Doing the heavy lifting was so time consuming and frustrating.

- In one or two sentences, describe how this project changed the way you think about AI generated code.
Ans: Honestly it has not really changed much, I am still scared and skeptical about creating a whole project with AI and I keep thinking about it messing everything up and me having to restart or me not being able to start over or even follow along anymore or even becoming lazy ^^ but this project changed me wanting to stick to this ideaology and become open to trying till I get to this point and I will cross the bridge but by then the world will not leave me behind at least!
