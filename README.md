# Meeseeks Box:
An interface allowing you to communicate with different large languages models (only chat-gpt supported currently) easily and allowing them to communicate with one another.

To interact with chat-gtp in the usual chat mode (plus some local commands) run 

`gpt-ping`

![demonstration of gpt-ping](ressources/images/gpt-ping_demo.gif)

## Requirements

Currently only works on linux (and possible MacOS)

requires the [`glow`](https://github.com/charmbracelet/glow) program for printing 


# Todo:
- [ ] Command help
- [ ] multi-meeseeks conversation
- [x] Terminal feedback
- [ ] Add hyperlinks to run command ?
- [ ] Summon other messeks
- [x] Make glow code block *blockier* 
- [x] Implement `stream` api
- [ ] Add a method to load conversation
- [x] Add a token counter
- [ ] Add other llm
- [ ] find a way to display images
- [ ] Make fancy printing optional

- Live mode:
	- [x] make live less bugy
	- [x] implement code parsing
    - [ ] fix 'too long line' bug
    - [x] live parsing for 'action' keywords
