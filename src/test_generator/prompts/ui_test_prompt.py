"""UI Test Prompt - JavaFX/Swing"""
UI_TEST_PROMPT = """
SPECIALIZATION: JavaFX/Swing UI Smoke Tests
Detection: JavaFX Application, JFrame, Swing components
Framework: TestFX for JavaFX, AssertJ-Swing for Swing
Approach: Launch app, verify main window appears, check critical UI components visible
"""
def get_ui_test_prompt(): return UI_TEST_PROMPT
