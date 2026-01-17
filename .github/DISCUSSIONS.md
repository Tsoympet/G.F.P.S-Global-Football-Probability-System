# GitHub Discussions Setup Guide

This document provides instructions for enabling and configuring GitHub Discussions for the G.F.P.S repository.

## Enabling Discussions

To enable GitHub Discussions for this repository:

1. Go to the repository Settings on GitHub
2. Scroll down to the "Features" section
3. Check the box next to "Discussions"
4. Click "Set up Discussions" if prompted

## Discussion Categories

We recommend setting up the following categories:

### 📢 Announcements
- **Description**: Important updates, releases, and news about G.F.P.S
- **Format**: Announcement (maintainers only can create)
- **Purpose**: Keep the community informed about project updates

### 💡 Ideas
- **Description**: Feature requests and enhancement proposals
- **Format**: Open discussion
- **Purpose**: Gather community feedback on potential improvements

### ❓ Q&A
- **Description**: Ask and answer questions about G.F.P.S
- **Format**: Question & Answer (can mark answers)
- **Purpose**: Help users troubleshoot and learn

### 🎯 Show and Tell
- **Description**: Share projects, use cases, and successes with G.F.P.S
- **Format**: Open discussion
- **Purpose**: Showcase community creativity and real-world usage

### 💬 General
- **Description**: General discussion about G.F.P.S and related topics
- **Format**: Open discussion
- **Purpose**: Community conversations that don't fit other categories

## Discussion Templates

Discussion templates are located in `.github/DISCUSSION_TEMPLATE/` and include:

- `announcements.yml` - Template for announcements
- `ideas.yml` - Template for feature ideas
- `q-and-a.yml` - Template for questions
- `show-and-tell.yml` - Template for showcasing projects
- `general.yml` - Template for general discussions

These templates help guide users to provide relevant information when starting a discussion.

## Moderation Guidelines

### For Maintainers

1. **Be Responsive**: Try to respond to questions and discussions in a timely manner
2. **Be Welcoming**: Make new contributors feel welcome
3. **Guide to Resources**: Point users to documentation when applicable
4. **Move to Issues**: If a discussion reveals a bug or confirmed feature, create an issue
5. **Mark Answers**: In Q&A, mark helpful answers to make them easier to find
6. **Lock When Needed**: Lock discussions that become off-topic or unproductive

### For Community Members

1. **Search First**: Before creating a new discussion, search for similar topics
2. **Be Respectful**: Treat others with respect and kindness
3. **Stay On Topic**: Keep discussions relevant to G.F.P.S
4. **Provide Context**: When asking questions, include environment details and what you've tried
5. **Help Others**: If you know the answer to a question, share your knowledge

## Converting Discussions to Issues

When a discussion reveals:
- A clear bug that needs to be fixed
- A feature request that has community consensus
- A documentation gap that needs addressing

Convert it to an issue:
1. Create a new issue referencing the discussion
2. Link back to the discussion in the issue description
3. Add a comment in the discussion pointing to the new issue

## Best Practices

### For Starting Discussions

- **Use descriptive titles**: Make it easy for others to find relevant discussions
- **Provide context**: Explain your use case or problem clearly
- **Be specific**: Include version numbers, environment details, and steps to reproduce
- **Add labels**: Use appropriate labels to categorize discussions
- **Follow templates**: Use the provided templates when applicable

### For Responding

- **Quote relevant parts**: Use quotes to reference specific points
- **Provide examples**: Code snippets or configuration examples are helpful
- **Link to docs**: Reference relevant documentation when applicable
- **Mark as answer**: If your question was answered, mark the helpful response
- **Follow up**: Update the discussion if you solve your problem

## Integration with Other Tools

### Issues
- Move confirmed bugs and feature requests to issues
- Reference discussions in issue descriptions
- Link back to discussions for context

### Pull Requests
- Reference relevant discussions in PR descriptions
- Notify discussion participants when implementing their ideas
- Use discussions to gather feedback before major changes

### Documentation
- Update documentation based on frequently asked questions
- Create guides for common use cases discovered in discussions
- Reference discussions in commit messages when addressing community feedback

## Metrics and Success

Track discussion health through:
- Response time to new questions
- Percentage of questions with accepted answers
- Community participation (not just maintainers)
- Conversion of ideas to implemented features
- Overall community sentiment

## Examples of Good Discussions

### Good Question
```
Title: [Question] How to configure custom team strength parameters?

I'm trying to set custom team strength multipliers for my league analysis.
I've reviewed the documentation in docs/BACKEND_GUIDE.md but I'm not sure
how to override the default parameters.

Environment:
- OS: Ubuntu 22.04
- G.F.P.S Version: v1.2.0
- Deployment: Docker

What I've tried:
- Setting TEAM_STRENGTH_MULTIPLIER in .env (doesn't seem to work)
- Modifying the config in backend/models/dixon_coles.py

Any guidance would be appreciated!
```

### Good Feature Idea
```
Title: [Feature Idea] Add support for Asian Handicap markets

Problem: Currently G.F.P.S focuses on 1X2 and totals markets, but Asian
Handicap is very popular in many regions and offers better odds in some cases.

Proposed Solution: Add a new market type for Asian Handicap with:
- Half-goal and quarter-goal handicaps
- Probability calculation based on goal distribution
- Integration with existing EV engine

Implementation: Could extend the existing Poisson model to calculate
probabilities for handicap scenarios.

Would this be something the maintainers would consider?
```

## Resources

- [GitHub Discussions Documentation](https://docs.github.com/en/discussions)
- [Managing Discussions](https://docs.github.com/en/discussions/managing-discussions-for-your-community)
- [Discussion Templates](https://docs.github.com/en/discussions/managing-discussions-for-your-community/creating-discussion-category-forms)

---

For questions about this setup, please open a discussion in the General category!
