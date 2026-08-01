import os
import sys
import time
import subprocess
from typing import Dict, Any

from vishai.kernel.planner.step import ExecutionStep
from vishai.utils.logger import SystemLogger

logger = SystemLogger.get_logger()

# Optional imports for Windows automation
try:
    import pyautogui
    # Failsafe and pause settings for safety
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except ImportError:
    pyautogui = None

try:
    if sys.platform == "win32":
        import pygetwindow as gw
    else:
        gw = None
except ImportError:
    gw = None

class OSControlCapability:
    """
    Capability responsible for direct OS-level execution.
    Provides Real Windows Automation for typing, clicking, and window management.
    """
    @property
    def name(self) -> str:
        return "os_control"
        
    def execute(self, step: ExecutionStep) -> Dict[str, Any]:
        """Performs OS operations requested in the ExecutionStep."""
        start_time = time.time()
        result = {
            "success": False,
            "reason": "",
            "execution_time": 0.0
        }
        
        try:
            if step.action == "launch":
                result.update(self._action_launch(step))
            elif step.action == "wait":
                result.update(self._action_wait(step))
            elif step.action == "focus":
                result.update(self._action_focus(step))
            elif step.action == "type":
                result.update(self._action_type(step))
            elif step.action == "search":
                result.update(self._action_search(step))
            elif step.action == "press":
                result.update(self._action_press(step))
            elif step.action == "hotkey":
                result.update(self._action_hotkey(step))
            elif step.action == "mouse_move":
                result.update(self._action_mouse_move(step))
            elif step.action == "left_click":
                result.update(self._action_click(step, button="left", clicks=1))
            elif step.action == "right_click":
                result.update(self._action_click(step, button="right", clicks=1))
            elif step.action == "double_click":
                result.update(self._action_click(step, button="left", clicks=2))
            elif step.action == "scroll":
                result.update(self._action_scroll(step))
            elif step.action == "screenshot":
                result.update(self._action_screenshot(step))
            else:
                result["reason"] = f"Capability [os_control] does not support action '{step.action}'"
                
        except Exception as e:
            logger.error(f"Capability [os_control] failed at action '{step.action}': {e}", exc_info=True)
            result["success"] = False
            result["reason"] = f"Error: {str(e)}"
            
        result["execution_time"] = time.time() - start_time
        return result

    def _action_launch(self, step: ExecutionStep) -> dict:
        display_name = step.parameters.get("display_name", step.target)
        logger.info(f"Capability [os_control] launching: {display_name} ({step.target})")
        if sys.platform == "win32":
            os.startfile(step.target)
            return {"success": True, "reason": f"Successfully requested OS to start {display_name}"}
        else:
            subprocess.Popen(
                [step.target], 
                start_new_session=True, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL, 
                stdin=subprocess.DEVNULL
            )
            return {"success": True, "reason": f"Successfully launched {display_name} in background"}

    def _action_wait(self, step: ExecutionStep) -> dict:
        duration = step.parameters.get("duration", 1.0)
        logger.info(f"Capability [os_control] waiting for {duration} seconds.")
        time.sleep(float(duration))
        return {"success": True, "reason": f"Waited for {duration} seconds"}

    def _action_focus(self, step: ExecutionStep) -> dict:
        window_title = step.parameters.get("window_title", step.target)
        logger.info(f"Capability [os_control] focusing window: {window_title}")
        
        if sys.platform == "win32" and gw is not None:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                win = windows[0]
                if not win.isActive:
                    win.activate()
                return {"success": True, "reason": f"Focused window '{win.title}'"}
            else:
                return {"success": False, "reason": f"Window with title '{window_title}' not found"}
        else:
            logger.warning("Focus window is mock implemented on non-Windows or when pygetwindow is missing.")
            return {"success": True, "reason": f"Mock focused window {window_title}"}

    def _action_type(self, step: ExecutionStep) -> dict:
        text = step.parameters.get("text", "")
        logger.info(f"Capability [os_control] typing text: {text}")
        if pyautogui:
            pyautogui.write(text, interval=0.01)
            return {"success": True, "reason": f"Typed text '{text}'"}
        return {"success": True, "reason": f"Mock typed text '{text}'"}

    def _action_search(self, step: ExecutionStep) -> dict:
        query = step.parameters.get("query", "")
        logger.info(f"Capability [os_control] executing search for: {query}")
        if pyautogui:
            pyautogui.write(query, interval=0.01)
            pyautogui.press("enter")
            return {"success": True, "reason": f"Typed search query '{query}' and pressed enter"}
        return {"success": True, "reason": f"Mock executed search for '{query}'"}

    def _action_press(self, step: ExecutionStep) -> dict:
        key = step.parameters.get("key", "")
        logger.info(f"Capability [os_control] pressing key: {key}")
        if pyautogui:
            pyautogui.press(key)
            return {"success": True, "reason": f"Pressed key '{key}'"}
        return {"success": True, "reason": f"Mock pressed key '{key}'"}

    def _action_hotkey(self, step: ExecutionStep) -> dict:
        keys = step.parameters.get("keys", [])
        if isinstance(keys, str):
            keys = [k.strip() for k in keys.split(",")]
        logger.info(f"Capability [os_control] pressing hotkey: {keys}")
        if pyautogui:
            pyautogui.hotkey(*keys)
            return {"success": True, "reason": f"Pressed hotkey {keys}"}
        return {"success": True, "reason": f"Mock pressed hotkey {keys}"}

    def _action_mouse_move(self, step: ExecutionStep) -> dict:
        x = step.parameters.get("x")
        y = step.parameters.get("y")
        duration = float(step.parameters.get("duration", 0.0))
        logger.info(f"Capability [os_control] moving mouse to: ({x}, {y})")
        if pyautogui and x is not None and y is not None:
            pyautogui.moveTo(int(x), int(y), duration=duration)
            return {"success": True, "reason": f"Moved mouse to ({x}, {y})"}
        return {"success": True, "reason": f"Mock moved mouse to ({x}, {y})"}

    def _action_click(self, step: ExecutionStep, button: str, clicks: int) -> dict:
        x = step.parameters.get("x")
        y = step.parameters.get("y")
        logger.info(f"Capability [os_control] clicking ({button}, {clicks} times) at ({x}, {y})")
        if pyautogui:
            if x is not None and y is not None:
                pyautogui.click(x=int(x), y=int(y), button=button, clicks=clicks)
            else:
                pyautogui.click(button=button, clicks=clicks)
            return {"success": True, "reason": f"Performed {button} click ({clicks}x)"}
        return {"success": True, "reason": f"Mock performed {button} click ({clicks}x)"}

    def _action_scroll(self, step: ExecutionStep) -> dict:
        amount = int(step.parameters.get("amount", 0))
        logger.info(f"Capability [os_control] scrolling by: {amount}")
        if pyautogui:
            pyautogui.scroll(amount)
            return {"success": True, "reason": f"Scrolled {amount}"}
        return {"success": True, "reason": f"Mock scrolled {amount}"}

    def _action_screenshot(self, step: ExecutionStep) -> dict:
        save_path = step.parameters.get("save_path", "screenshot.png")
        logger.info(f"Capability [os_control] taking screenshot saved to: {save_path}")
        if pyautogui:
            img = pyautogui.screenshot()
            img.save(save_path)
            return {"success": True, "reason": f"Saved screenshot to {save_path}"}
        return {"success": True, "reason": f"Mock saved screenshot to {save_path}"}
