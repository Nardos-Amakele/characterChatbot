class EmotionEngine:
    def __init__(self):
        # Initialize with Psi Theory defaults
        self.base_state = {
            "valence": 0.5,               # -1 (aversion) to +1 (appetence)
            "arousal": 0.5,               # 0 (passive) to 1 (active)
            "selection_threshold": 0.7,   # Higher = less motive shifting
            "resolution_level": 0.6,      # 0 (broad) to 1 (detailed)
            "goal_directedness": 0.8,     # 0 (adaptive) to 1 (goal-focused)
            "securing_rate": 0.4,         # 0 (rare checks) to 1 (frequent)
            "emotion": "neutral"         # Mapped from parameters
        }

    def update_state(self, message, traits, history):
        """Update Psi parameters based on interaction"""
        state = self.base_state.copy()
        
        # Calculate impact factors
        intensity = min(1.0, len(message) / 50)
        positive_triggers = ["love", "happy", "good", *traits]
        negative_triggers = ["hate", "angry", "bad", "no"]
        
        # Valence (positive/negative)
        if any(word in message.lower() for word in positive_triggers):
            state["valence"] = min(1.0, state["valence"] + 0.3 * intensity)
        if any(word in message.lower() for word in negative_triggers):
            state["valence"] = max(-1.0, state["valence"] - 0.3 * intensity)
        
        # Arousal (action readiness)
        excl_count = message.count('!')
        ques_count = message.count('?')
        state["arousal"] = min(1.0, state["arousal"] + 0.1 * (excl_count + ques_count))
        
        # Goal-directedness (stability vs. adaptability)
        if "why" in message.lower() or "?" in message:
            state["goal_directedness"] = max(0.1, state["goal_directedness"] - 0.1)
        
        # Map to emotions
        state["emotion"] = self._map_emotion(state)
        return state

    def _map_emotion(self, state):
        """Map Psi parameters to emotions (Anger, Sadness, etc.)"""
        if state["valence"] < -0.7 and state["arousal"] > 0.7:
            return "anger"
        elif state["valence"] < -0.5 and state["arousal"] < 0.3:
            return "sadness"
        elif state["valence"] > 0.7 and state["arousal"] > 0.6:
            return "joy"
        elif state["valence"] > 0.8 and state["arousal"] < 0.2:
            return "bliss"
        elif state["selection_threshold"] > 0.8:
            return "pride"
        else:
            return "neutral"