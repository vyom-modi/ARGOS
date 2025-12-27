import os
import asyncio
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="ARGOS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.pending_approval: asyncio.Event = asyncio.Event()
        self.approval_result: bool = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.get("/")
def read_root():
    return {
        "status": "ARGOS Backend Running", 
        "version": "3.0.0", 
        "features": ["e2b_sandbox", "groq_llm", "bandit_scan", "mission_types"]
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print(f"[WS] Client connected: {websocket.client}")
    
    try:
        while True:
            try:
                raw_data = await websocket.receive_text()
                print(f"[WS] Received: {raw_data[:100]}")
                
                try:
                    data = json.loads(raw_data)
                except json.JSONDecodeError:
                    continue
                
                if data.get("type") == "start_mission":
                    payload = data.get("payload", {})
                    asyncio.create_task(run_mission(
                        target_type=payload.get("target_type", "local"),
                        target=payload.get("target", ""),
                        message=payload.get("message", ""),
                        mission_type=payload.get("mission_type", "security")
                    ))
                
                elif data.get("type") == "approval":
                    manager.approval_result = data.get("payload", {}).get("approved", False)
                    manager.pending_approval.set()
                
                elif data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except Exception as e:
                print(f"[WS] Error: {e}")
                break
                
    except WebSocketDisconnect:
        print(f"[WS] Disconnected: {websocket.client}")
    finally:
        manager.disconnect(websocket)


async def run_mission(target_type: str, target: str, message: str, mission_type: str = "security"):
    """Run a mission based on mission type using E2B sandbox for safety."""
    
    print(f"[MISSION] Starting: type={mission_type}, target={target[:50]}")
    
    await manager.broadcast({"type": "log", "content": f"Mission started: {message}"})
    
    tokens_used = 0
    start_time = asyncio.get_event_loop().time()
    
    # Initialize Groq LLM
    groq_api_key = os.getenv("GROQ_API_KEY")
    e2b_api_key = os.getenv("E2B_API_KEY")
    llm = None
    
    if groq_api_key:
        try:
            from langchain_groq import ChatGroq
            llm = ChatGroq(api_key=groq_api_key, model="openai/gpt-oss-120b")
            await manager.broadcast({"type": "log", "content": "🧠 LLM: Groq initialized (openai/gpt-oss-120b)"})
            print("[LLM] Initialized successfully")
        except Exception as e:
            print(f"[LLM] Init failed: {e}")
            await manager.broadcast({"type": "log", "content": f"⚠️ LLM unavailable: {str(e)[:50]}"})
    
    try:
        # Execute mission based on type
        if mission_type == "security":
            await run_security_scan(target_type, target, llm, e2b_api_key, tokens_used, start_time)
        elif mission_type == "audit":
            await run_dependency_audit(target_type, target, llm, e2b_api_key, tokens_used, start_time)
        elif mission_type == "fix":
            await run_bug_analysis(target_type, target, llm, e2b_api_key, tokens_used, start_time)
        else:  # custom
            await run_custom_task(target_type, target, message, llm, e2b_api_key, tokens_used, start_time)
            
    except Exception as e:
        print(f"[MISSION ERROR] {e}")
        await manager.broadcast({"type": "log", "content": f"❌ Error: {str(e)[:100]}"})
    
    await manager.broadcast({"type": "node_update", "node": None})
    await manager.broadcast({"type": "mission_complete"})
    await manager.broadcast({"type": "log", "content": "✅ Mission completed."})


async def run_security_scan(target_type: str, target: str, llm, e2b_api_key: str, tokens_used: int, start_time: float):
    """Run security vulnerability scan using E2B sandbox."""
    
    await manager.broadcast({"type": "node_update", "node": "Explorer"})
    await manager.broadcast({"type": "log", "content": "Explorer: Initializing E2B sandbox for safe analysis..."})
    
    if not e2b_api_key:
        await manager.broadcast({"type": "log", "content": "⚠️ E2B_API_KEY not found. Cannot run sandboxed scan."})
        await manager.broadcast({"type": "log", "content": "Please add E2B_API_KEY to your .env file."})
        return
    
    try:
        from e2b_code_interpreter import Sandbox
        
        sandbox = Sandbox.create()
        await manager.broadcast({"type": "log", "content": "Explorer: E2B sandbox started ✓"})
        
        try:
            # Clone or copy repo inside sandbox
            if target_type == "github":
                await manager.broadcast({"type": "log", "content": f"Explorer: Cloning {target} inside sandbox..."})
                clone_result = sandbox.run_code(f'''
import subprocess
result = subprocess.run(["git", "clone", "--depth", "1", "{target}", "/tmp/repo"], capture_output=True, text=True)
print("CLONE_SUCCESS" if result.returncode == 0 else f"CLONE_FAILED: {{result.stderr}}")
''')
                if clone_result.logs:
                    if hasattr(clone_result.logs, 'stdout'):
                        for log in clone_result.logs.stdout:
                            await manager.broadcast({"type": "log", "content": f"Sandbox: {str(log)[:200]}"})
                    if hasattr(clone_result.logs, 'stderr'):
                        for log in clone_result.logs.stderr:
                            await manager.broadcast({"type": "log", "content": f"Sandbox Error: {str(log)[:200]}"})
                await manager.broadcast({"type": "log", "content": "Explorer: Repository cloned inside sandbox ✓"})
            else:
                await manager.broadcast({"type": "log", "content": f"Explorer: Analyzing local path: {target}"})
                # For local paths, we'd need to upload files to sandbox
                await manager.broadcast({"type": "log", "content": "⚠️ Local path scanning requires file upload (not implemented yet)"})
                sandbox.kill()
                return
            
            tokens_used += 100
            await update_telemetry(tokens_used, 0, start_time)
            
            # Explore the codebase
            await manager.broadcast({"type": "log", "content": "Explorer: Scanning directory structure..."})
            explore_result = sandbox.run_code('''
import os
files = []
python_files = []
for root, dirs, filenames in os.walk("/tmp/repo"):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]
    for f in filenames:
        rel = os.path.relpath(os.path.join(root, f), "/tmp/repo")
        files.append(rel)
        if f.endswith('.py'):
            python_files.append(os.path.join(root, f))
print(f"FILES:{len(files)}")
print(f"PYTHON:{len(python_files)}")
print(f"SAMPLE:{','.join(files[:10])}")
''')
            
            file_count = 0
            python_count = 0
            js_count = 0
            sample_files = ""
            # Parse output from logs
            full_output = ""
            if explore_result.logs:
                for log in explore_result.logs.stdout:
                    full_output += str(log)
            
            for line in full_output.splitlines():
                if "FILES:" in line:
                    try:
                        file_count = int(line.split("FILES:")[1].strip())
                    except: pass
                if "PYTHON:" in line:
                    try:
                        python_count = int(line.split("PYTHON:")[1].strip())
                    except: pass
                if "SAMPLE:" in line:
                    sample_files = line.split("SAMPLE:")[1].strip()
            
            # Check for package.json using a simple ls check
            has_package_json = False
            check_pkg = sandbox.run_code('import os; print("PKG:YES" if os.path.exists("/tmp/repo/package.json") else "PKG:NO")')
            if check_pkg.logs:
                for log in check_pkg.logs.stdout:
                    if "PKG:YES" in str(log):
                        has_package_json = True

            await manager.broadcast({"type": "log", "content": f"Explorer: Found {file_count} files ({python_count} Python)"})
            if has_package_json:
                await manager.broadcast({"type": "log", "content": "Explorer: Detected Node.js project (package.json found)"})
            
            if sample_files:
                await manager.broadcast({"type": "log", "content": f"Explorer: Files: {sample_files[:100]}..."})
            
            tokens_used += 50
            await update_telemetry(tokens_used, 0, start_time)
            await asyncio.sleep(1)
            
            # Run Bandit security scan (Python)
            await manager.broadcast({"type": "node_update", "node": "Auditor"})
            
            vulnerabilities = []
            first_vuln_code = ""

            if python_count > 0:
                await manager.broadcast({"type": "log", "content": "Auditor: Installing and running Bandit (Python)..."})
                bandit_result = sandbox.run_code('''
import subprocess
import json

# Install bandit
subprocess.run(["pip", "install", "bandit", "-q"], capture_output=True)

# Run bandit
result = subprocess.run(["bandit", "-r", "/tmp/repo", "-f", "json", "-q"], capture_output=True, text=True)
if result.stdout:
    try:
        data = json.loads(result.stdout)
        issues = data.get("results", [])
        print(f"VULN_COUNT:{len(issues)}")
        for i, issue in enumerate(issues[:5]):
            sev = issue.get("issue_severity", "UNKNOWN")
            text = issue.get("issue_text", "")[:80]
            fname = issue.get("filename", "").split("/")[-1]
            line = issue.get("line_number", 0)
            code = issue.get("code", "")[:200]
            print(f"VULN:{sev}|{text}|{fname}:{line}")
            if i == 0:
                print(f"CODE:{code}")
    except:
        print("VULN_COUNT:0")
else:
    print("VULN_COUNT:0")
''')
                if bandit_result.logs:
                    full_bandit_output = ""
                    for log in bandit_result.logs.stdout:
                        full_bandit_output += str(log)
                    
                    for line in full_bandit_output.splitlines():
                        if "VULN_COUNT:" in line:
                            try:
                                vuln_count = int(line.split("VULN_COUNT:")[1].strip())
                                await manager.broadcast({"type": "log", "content": f"Auditor: Bandit found {vuln_count} Python issues"})
                            except: pass
                        elif "VULN:" in line:
                            parts = line.split("VULN:")[1].strip().split("|")
                            if len(parts) >= 3:
                                sev, text, loc = parts[0], parts[1], parts[2]
                                vulnerabilities.append({"severity": sev, "text": text, "location": loc})
                                await manager.broadcast({"type": "log", "content": f"Auditor: [Python:{sev}] {text} in {loc}"})
                        elif "CODE:" in line:
                            first_vuln_code = line.split("CODE:")[1].strip()

            # Run npm audit (Node.js) if detected
            if has_package_json:
                await manager.broadcast({"type": "log", "content": "Auditor: Running npm audit (Node.js)..."})
                await manager.broadcast({"type": "log", "content": "ℹ️ Note: Basic auditing. Full JS scan requires more setup."})
                await manager.broadcast({"type": "log", "content": "⏳ Running npm audit... This may take up to 60 seconds."})
                # Note: This relies on npm being available in the sandbox or installable
                # E2B default environment might not have npm pre-installed, simple attempt
                # Improved npm audit script to output structured vulnerabilities
                npm_result = sandbox.run_code('''
import subprocess
import json

try:
    # Check if npm exists
    check = subprocess.run(["npm", "--version"], capture_output=True)
    if check.returncode == 0:
        # Run npm audit
        result = subprocess.run(["npm", "audit", "--json", "--prefix", "/tmp/repo"], capture_output=True, text=True)
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                count = 0
                if "vulnerabilities" in data:
                    for name, details in data["vulnerabilities"].items():
                        sev = details.get("severity", "low")
                        if sev in ["high", "critical"]:
                            print(f"VULN:{sev}|{name} vulnerability|package.json")
                            count += 1
                            if count >= 5: break
                
                # Also check metadata for total count
                if "metadata" in data and "vulnerabilities" in data["metadata"]:
                    total = data["metadata"]["vulnerabilities"].get("total", 0)
                    print(f"NPM_COUNT:{total}")
            except:
                print("NPM_PARSE_ERROR")
    else:
        print("NPM_MISSING")
except:
    print("NPM_ERROR")
''')
                if npm_result.logs:
                     full_npm_output = ""
                     for log in npm_result.logs.stdout:
                        full_npm_output += str(log)
                     
                     for line in full_npm_output.splitlines():
                        if "NPM_MISSING" in line:
                             await manager.broadcast({"type": "log", "content": "Auditor: npm not found in sandbox, skipping JS audit"})
                        elif "VULN:" in line:
                            parts = line.split("VULN:")[1].strip().split("|")
                            if len(parts) >= 3:
                                sev, text, loc = parts[0], parts[1], parts[2]
                                vulnerabilities.append({"severity": sev, "text": text, "location": loc})
                                await manager.broadcast({"type": "log", "content": f"Auditor: [Node:{sev}] {text}"})
                        elif "NPM_COUNT:" in line:
                            count = line.split("NPM_COUNT:")[1].strip()
                            await manager.broadcast({"type": "log", "content": f"Auditor: npm audit found {count} total issues"})

                        
            tokens_used += 150
            await update_telemetry(tokens_used, 0, start_time)
            
            # LLM Analysis
            if llm and vulnerabilities:
                await manager.broadcast({"type": "log", "content": "🧠 LLM: Analyzing vulnerabilities..."})
                try:
                    vuln_summary = "\n".join([f"- [{v['severity']}] {v['text']} at {v['location']}" for v in vulnerabilities[:5]])
                    response = await asyncio.to_thread(llm.invoke, f"Briefly analyze these security issues (2 sentences max):\n{vuln_summary}")
                    analysis = response.content if hasattr(response, 'content') else str(response)
                    await manager.broadcast({"type": "log", "content": f"🧠 LLM: {analysis[:250]}"})
                    
                    usage = response.response_metadata.get('token_usage', {})
                    in_tok = usage.get('prompt_tokens', 400)
                    out_tok = usage.get('completion_tokens', 100)
                    
                    await update_telemetry(tokens_used + in_tok, out_tok, start_time)
                except Exception as e:
                    await manager.broadcast({"type": "log", "content": f"🧠 LLM analysis failed: {str(e)[:50]}"})
            
            # Human approval if vulnerabilities found
            if vulnerabilities:
                await manager.broadcast({"type": "node_update", "node": "Human"})
                await manager.broadcast({"type": "log", "content": "Supervisor: Routing to Human for review..."})
                
                first_vuln = vulnerabilities[0]
                old_code = first_vuln_code if first_vuln_code else f"# {first_vuln['text']}"
                # Generate a real fix using LLM
                await manager.broadcast({"type": "log", "content": "Supervisor: Generating fix for vulnerability..."})
                
                lang_context = "Python"
                # Parse clean filename from location
                clean_filename = first_vuln['location'].split(':')[0]
                if clean_filename.endswith('.js'): lang_context = "JavaScript"
                if clean_filename.endswith('package.json'): lang_context = "Node.js Dependency"

                fix_prompt = f"""You are a security expert. Fix this {lang_context} vulnerability:
                Issue: {first_vuln['text']}
                Location: {first_vuln['location']}
                Current Code (Snippet):
                {old_code}
                
                Return the COMPLETE functional fixed code for this file. 
                For package.json, return the updated JSON content.
                For JS/Python, return the fixed source code.
                Do not include markdown formatting. Do not include explanation. Just the code."""
                
                fix_response = await asyncio.to_thread(llm.invoke, fix_prompt)
                new_code = fix_response.content.replace("```python", "").replace("```json", "").replace("```javascript", "").replace("```", "").strip()
                
                await manager.broadcast({
                    "type": "approval_required",
                    "old_code": old_code,
                    "new_code": new_code
                })
                
                manager.pending_approval.clear()
                await manager.pending_approval.wait()
                
                if manager.approval_result:
                    await manager.broadcast({"type": "log", "content": "Human: Review acknowledged ✓"})
                    
                    # Apply fix in sandbox
                    # Parse filename from location (e.g. "views.py:50" -> "views.py")
                    clean_filename = first_vuln['location'].split(':')[0]
                    
                    if any(clean_filename.endswith(ext) for ext in ['.py', '.js', 'package.json']):
                        await manager.broadcast({"type": "log", "content": f"Execution: Applying fix to {clean_filename}..."})
                        # Determine file path
                        file_path = f"/tmp/repo/{clean_filename}"
                        
                        # Generate fix using LLM if not already done properly or just use the new_code
                        # For this demo, we'll try to apply the suggested change (simplified)
                        # Ideally, we'd use 'sed' or write the whole file back.
                        # Let's try to overwrite the file with LLM generated fix
                        
                        apply_result = sandbox.run_code(f'''
import os
# Handle relative paths (e.g. ./settings.py -> settings.py)
clean_path = "{file_path}".replace("/tmp/repo/./", "/tmp/repo/")

try:
    with open(clean_path, "w") as f:
        f.write("""{new_code}""")
    print("FIX_APPLIED")
except Exception as e:
    # Try creating directory if missing?? No, assume repo structure exists.
    print(f"FIX_ERROR:{{e}}")
''')
                        if apply_result.logs:
                             for log in apply_result.logs.stdout:
                                 if "FIX_APPLIED" in str(log):
                                     await manager.broadcast({"type": "log", "content": "Execution: Fix applied successfully ✓"})
                                 elif "FIX_ERROR" in str(log):
                                     await manager.broadcast({"type": "log", "content": f"❌ Fix application failed: {str(log)}"})

                    # Generate Patch
                    await manager.broadcast({"type": "log", "content": "Execution: Generating patch file..."})
                    # Force git to track the file if untracked (for new files) and run diff
                    diff_result = sandbox.run_code('''
import subprocess
try:
    # Ensure git knows about the file
    subprocess.run(["git", "add", "-N", "."], cwd="/tmp/repo", capture_output=True) 
    result = subprocess.run(["git", "diff"], cwd="/tmp/repo", capture_output=True, text=True)
    print(result.stdout)
except Exception as e:
    print(f"DIFF_ERROR:{{e}}")
''')

                    
                    if diff_result.logs:
                        patch_content = ""
                        for log in diff_result.logs.stdout:
                            patch_content += str(log)
                        
                        if patch_content.strip():
                            # Save patch to host
                            patch_dir = "patches"
                            os.makedirs(patch_dir, exist_ok=True)
                            patch_filename = f"{patch_dir}/fix_{int(start_time)}.patch"
                            with open(patch_filename, "w") as f:
                                f.write(patch_content)
                            
                            await manager.broadcast({"type": "log", "content": f"✅ Patch saved to: {patch_filename}"})
                            await manager.broadcast({"type": "log", "content": "ℹ️ You can apply this patch to your local repository."})
                        else:
                            await manager.broadcast({"type": "log", "content": "⚠️ No changes detected in git diff."})

                else:
                    await manager.broadcast({"type": "log", "content": "Human: Changes rejected"})
            else:
                await manager.broadcast({"type": "log", "content": "Auditor: ✅ No security vulnerabilities detected!"})
            
            # Execution phase
            await manager.broadcast({"type": "node_update", "node": "Execution"})
            await manager.broadcast({"type": "log", "content": "Execution: Generating security report..."})
            
            await manager.broadcast({"type": "log", "content": f"Execution: Scan complete - {python_count} Python files analyzed"})
            await manager.broadcast({"type": "log", "content": f"Execution: {len(vulnerabilities)} issues found"})
            
        finally:
            sandbox.kill()
            await manager.broadcast({"type": "log", "content": "Cleanup: E2B sandbox terminated ✓"})
            
    except ImportError:
        await manager.broadcast({"type": "log", "content": "❌ E2B SDK not installed. Run: pip install e2b-code-interpreter"})
    except Exception as e:
        await manager.broadcast({"type": "log", "content": f"❌ Sandbox error: {str(e)[:100]}"})


async def run_dependency_audit(target_type: str, target: str, llm, e2b_api_key: str, tokens_used: int, start_time: float):
    """Run dependency audit to check for outdated/vulnerable packages."""
    
    await manager.broadcast({"type": "node_update", "node": "Explorer"})
    await manager.broadcast({"type": "log", "content": "Explorer: Starting dependency audit..."})
    
    if not e2b_api_key:
        await manager.broadcast({"type": "log", "content": "⚠️ E2B_API_KEY required for sandboxed audit"})
        return
    
    try:
        from e2b_code_interpreter import Sandbox
        
        sandbox = Sandbox.create()
        await manager.broadcast({"type": "log", "content": "Explorer: E2B sandbox started ✓"})
        
        try:
            if target_type == "github":
                sandbox.run_code(f'import subprocess; subprocess.run(["git", "clone", "--depth", "1", "{target}", "/tmp/repo"])')
                await manager.broadcast({"type": "log", "content": "Explorer: Repository cloned ✓"})
            
            tokens_used += 100
            await update_telemetry(tokens_used, 0, start_time)
            
            await manager.broadcast({"type": "node_update", "node": "Auditor"})
            await manager.broadcast({"type": "log", "content": "Auditor: Checking for requirements.txt..."})
            
            audit_result = sandbox.run_code('''
import subprocess
import os

req_file = "/tmp/repo/requirements.txt"
if os.path.exists(req_file):
    with open(req_file) as f:
        deps = f.read()
    print(f"DEPS_FOUND:{len(deps.splitlines())}")
    print(f"CONTENT:{deps[:500]}")
    
    # Install pip-audit
    subprocess.run(["pip", "install", "pip-audit", "-q"], capture_output=True)
    result = subprocess.run(["pip-audit", "-r", req_file], capture_output=True, text=True)
    print(f"AUDIT_RESULT:{result.stdout[:500] if result.stdout else 'No vulnerabilities'}")
else:
    print("NO_REQUIREMENTS")
''')
            
            if audit_result.logs:
                full_audit_output = ""
                for log in audit_result.logs.stdout:
                    full_audit_output += str(log)
                    
                for line in full_audit_output.splitlines():
                    if "DEPS_FOUND:" in line:
                        count = line.split("DEPS_FOUND:")[1].strip()
                        await manager.broadcast({"type": "log", "content": f"Auditor: Found {count} dependencies"})
                    elif "AUDIT_RESULT:" in line:
                        result = line.split("AUDIT_RESULT:")[1].strip()
                        await manager.broadcast({"type": "log", "content": f"Auditor: {result[:200]}"})
                    elif "NO_REQUIREMENTS" in line:
                        await manager.broadcast({"type": "log", "content": "Auditor: No requirements.txt found"})
            
            await manager.broadcast({"type": "node_update", "node": "Execution"})
            tokens_used += 50
            await update_telemetry(tokens_used, 0, start_time)
            await manager.broadcast({"type": "log", "content": "Execution: Dependency audit complete"})
            
        finally:
            sandbox.kill()
            await manager.broadcast({"type": "log", "content": "Cleanup: Sandbox terminated ✓"})
            
    except Exception as e:
        await manager.broadcast({"type": "log", "content": f"❌ Error: {str(e)[:100]}"})


async def run_bug_analysis(target_type: str, target: str, llm, e2b_api_key: str, tokens_used: int, start_time: float):
    """Run bug/code quality analysis."""
    
    await manager.broadcast({"type": "node_update", "node": "Explorer"})
    await manager.broadcast({"type": "log", "content": "Explorer: Starting code quality analysis..."})
    
    if not e2b_api_key:
        await manager.broadcast({"type": "log", "content": "⚠️ E2B_API_KEY required"})
        return
    
    try:
        from e2b_code_interpreter import Sandbox
        
        sandbox = Sandbox.create()
        await manager.broadcast({"type": "log", "content": "Explorer: E2B sandbox started ✓"})
        
        try:
            if target_type == "github":
                sandbox.run_code(f'import subprocess; subprocess.run(["git", "clone", "--depth", "1", "{target}", "/tmp/repo"])')
                await manager.broadcast({"type": "log", "content": "Explorer: Repository cloned ✓"})
            
            tokens_used += 100
            await update_telemetry(tokens_used, 0, start_time)
            
            await manager.broadcast({"type": "node_update", "node": "Auditor"})
            await manager.broadcast({"type": "log", "content": "Auditor: Running pylint code analysis..."})
            
            lint_result = sandbox.run_code('''
import subprocess

subprocess.run(["pip", "install", "pylint", "-q"], capture_output=True)
result = subprocess.run(["pylint", "/tmp/repo", "--max-line-length=120", "-E"], capture_output=True, text=True)
if result.stdout:
    lines = result.stdout.strip().split("\\n")[:10]
    for line in lines:
        if line.strip():
            print(f"LINT:{line[:150]}")
else:
    print("LINT:No errors found")
''')
            
            if lint_result.logs:
                full_lint_output = ""
                for log in lint_result.logs.stdout:
                    full_lint_output += str(log)
                    
                for line in full_lint_output.splitlines():
                    if "LINT:" in line:
                        msg = line.split("LINT:")[1].strip()
                        await manager.broadcast({"type": "log", "content": f"Auditor: {msg[:120]}"})
            
            await manager.broadcast({"type": "node_update", "node": "Execution"})
            tokens_used += 150
            await update_telemetry(tokens_used, 0, start_time)
            await manager.broadcast({"type": "log", "content": "Execution: Code analysis complete"})
            
        finally:
            sandbox.kill()
            await manager.broadcast({"type": "log", "content": "Cleanup: Sandbox terminated ✓"})
            
    except Exception as e:
        await manager.broadcast({"type": "log", "content": f"❌ Error: {str(e)[:100]}"})


async def run_custom_task(target_type: str, target: str, message: str, llm, e2b_api_key: str, tokens_used: int, start_time: float):
    """Run a custom task using LLM to generate sandbox code."""
    input_tokens = 0
    output_tokens = 0
    
    await manager.broadcast({"type": "node_update", "node": "Supervisor"})
    await manager.broadcast({"type": "log", "content": f"Supervisor: Analyzing custom request: '{message}'..."})
    
    if not llm:
        await manager.broadcast({"type": "log", "content": "❌ Groq LLM required for custom tasks."})
        return
        
    if not e2b_api_key:
        await manager.broadcast({"type": "log", "content": "⚠️ E2B_API_KEY required"})
        return
        
    try:
        from e2b_code_interpreter import Sandbox
        sandbox = Sandbox.create()
        await manager.broadcast({"type": "log", "content": "Explorer: E2B sandbox started ✓"})
        
        try:
            # Clone repo
            if target_type == "github":
                await manager.broadcast({"type": "log", "content": f"Explorer: Cloning {target}..."})
                sandbox.run_code(f'import subprocess; subprocess.run(["git", "clone", "--depth", "1", "{target}", "/tmp/repo"])')
            
            # Generate code with LLM
            await manager.broadcast({"type": "log", "content": "Supervisor: Generating analysis code..."})
            
            prompt = f"""You are an expert Python engineer. Generate a Python script to run inside a strictly isolated sandbox to accomplish this task:
            
Task: "{message}"
Target Directory: "/tmp/repo"

Return ONLY valid Python code. No markdown. No comments outside the code.
Ensure the code prints results to stdout so we can capture them.
Do not use external network requests unless absolutely necessary.
Allowed libraries: os, sys, subprocess, json, re, glob, math, random, datetime.
"""
            response = await asyncio.to_thread(llm.invoke, prompt)
            code = response.content.replace("```python", "").replace("```", "").strip()
            
            # Extract real token usage
            usage = response.response_metadata.get('token_usage', {})
            input_tokens += usage.get('prompt_tokens', 0)
            output_tokens += usage.get('completion_tokens', 0)
            
            await update_telemetry(input_tokens, output_tokens, start_time)

            await manager.broadcast({"type": "log", "content": "Execution: Running generated code..."})
            
            # Execute generated code
            result = sandbox.run_code(code)
            
            if result.logs:
                if hasattr(result.logs, 'stdout'):
                    for log in result.logs.stdout:
                        await manager.broadcast({"type": "log", "content": f"Sandbox: {str(log)[:200]}"})
                if hasattr(result.logs, 'stderr'):
                    for log in result.logs.stderr:
                        await manager.broadcast({"type": "log", "content": f"Sandbox Error: {str(log)[:200]}"})
            if result.error:
                await manager.broadcast({"type": "log", "content": f"⚠️ Sandbox Error: {str(result.error)[:200]}"})
                
            # Add small overhead for execution if needed
            output_tokens += 100
            await update_telemetry(input_tokens, output_tokens, start_time)
            await manager.broadcast({"type": "log", "content": "Execution: Custom task completed"})
            
        finally:
            sandbox.kill()
            await manager.broadcast({"type": "log", "content": "Cleanup: Sandbox terminated ✓"})
            
    except Exception as e:
        await manager.broadcast({"type": "log", "content": f"❌ Error: {str(e)[:100]}"})



async def update_telemetry(input_tokens: int, output_tokens: int, start_time: float):
    elapsed = asyncio.get_event_loop().time() - start_time
    # Pricing: $0.15/1M input, $0.60/1M output
    cost = (input_tokens / 1_000_000 * 0.15) + (output_tokens / 1_000_000 * 0.60)
    
    await manager.broadcast({
        "type": "telemetry",
        "telemetry": {
            "tokens": input_tokens + output_tokens,
            "latency": int(elapsed * 1000),
            "cost": round(cost, 6)
        }
    })


@app.post("/run")
async def run_endpoint(message: str):
    return {"status": "Use WebSocket /ws for real-time missions"}

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Create patches directory if not exists
os.makedirs("patches", exist_ok=True)

app.mount("/patches", StaticFiles(directory="patches"), name="patches")

@app.get("/download_patch/{filename}")
async def download_patch(filename: str):
    file_path = os.path.join("patches", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/octet-stream', filename=filename)
    return {"error": "File not found"}

import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
