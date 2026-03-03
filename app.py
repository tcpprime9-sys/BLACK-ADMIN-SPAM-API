# DeVloped By AbdeeLkarim Amiri
# Updated for OB52 - version 1.120.1 (2019119621)
# Converted to Flask API by request
import requests
import os
import psutil
import sys
import jwt
import pickle
import json
import binascii
import time
import urllib3
import xKEys
import base64
import datetime
import re
import socket
import threading
import http.client
import ssl
import gzip
import asyncio
import gc
import uuid
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from io import BytesIO
from protobuf_decoder.protobuf_decoder import Parser
from xC4 import *
from datetime import datetime, timedelta
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from cfonts import render, say
from rich.console import Console
from rich.panel import Panel
from rich.align import Align

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
console = Console()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Store active spam sessions
active_sessions = {}
session_lock = threading.Lock()

def G_AccEss(U, P):
    """Get Garena access token"""
    UrL = "https://100067.connect.garena.com/oauth/guest/token/grant"
    HE = {
        "Host": "100067.connect.garena.com",
        "User-Agent": Ua(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }
    dT = {
        "uid": f"{U}",
        "password": f"{P}",
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067",
    }
    try:
        R = requests.post(UrL, headers=HE, data=dT)
        if R.status_code == 200:
            return R.json()["access_token"], R.json()["open_id"]
        else:
            print(R.json())
            return None, None
    except Exception as e:
        print(e)
        return None, None

def MajorLoGin(PyL):
    """Perform major login"""
    context = ssl._create_unverified_context()
    conn = http.client.HTTPSConnection("loginbp.ggblueshark.com", context=context)
    headers = {
        "X-Unity-Version": "2018.4.11f1",
        "ReleaseVersion": "OB52",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-GA": "v1 1",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)",
        "Host": "loginbp.ggblueshark.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
    }
    try:
        conn.request("POST", "/MajorLogin", body=PyL, headers=headers)
        response = conn.getresponse()
        raw_data = response.read()
        if response.getheader("Content-Encoding") == "gzip":
            with gzip.GzipFile(fileobj=BytesIO(raw_data)) as f:
                raw_data = f.read()
        TexT = raw_data.decode(errors="ignore")
        if "BR_PLATFORM_INVALID_OPENID" in TexT or "BR_GOP_TOKEN_AUTH_FAILED" in TexT:
            return None
        return raw_data.hex() if response.status in [200, 201] else None
    finally:
        conn.close()

class FF_Spammer:
    """Free Fire Spammer Class"""
    def __init__(self, uid, password, target_uid, session_id):
        self.uid = uid
        self.password = password
        self.target_uid = target_uid
        self.session_id = session_id
        self.running = False
        self.message_count = 0
        self.reader = None
        self.writer = None
        self.reader2 = None
        self.writer2 = None
        
    def stop(self):
        """Stop the spammer"""
        self.running = False
        
    async def start_spam(self):
        """Start spamming the target"""
        try:
            # Get tokens and connection info
            token_info = self.get_tokens()
            if not token_info:
                return False
                
            self.JwT_ToKen, self.key, self.iv, self.Timestamp, self.ip, self.port, self.ip2, self.port2, self.bot_uid = token_info
            
            # Create auth token
            self.create_auth_token()
            
            # Start spam loop for 10 minutes
            start_time = time.time()
            self.running = True
            
            while self.running and (time.time() - start_time) < 600:  # 10 minutes
                try:
                    await self.spam_cycle()
                except Exception as e:
                    print(f"Spam cycle error: {e}")
                    await asyncio.sleep(1)
                    
            return True
            
        except Exception as e:
            print(f"Spam start error: {e}")
            return False
        finally:
            await self.cleanup()
            
    async def spam_cycle(self):
        """Single spam cycle"""
        R = asyncio.Event()
        
        # Start chat connection
        chat_task = asyncio.create_task(
            self.chat_spam(self.JwT_ToKen, self.AutH_ToKen, self.ip, self.port, 
                          self.key, self.iv, self.bot_uid, R)
        )
        
        await R.wait()  # Wait for connection ready
        
        # Start online connection
        online_task = asyncio.create_task(
            self.online_keepalive(self.JwT_ToKen, self.AutH_ToKen, self.ip2, self.port2, 
                                 self.key, self.iv, self.bot_uid)
        )
        
        # Let it run for a while
        await asyncio.sleep(5)
        
        # Cleanup
        chat_task.cancel()
        online_task.cancel()
        await self.cleanup()
        
    async def cleanup(self):
        """Clean up connections"""
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except:
                pass
        if self.writer2:
            try:
                self.writer2.close()
                await self.writer2.wait_closed()
            except:
                pass
        self.reader = None
        self.writer = None
        self.reader2 = None
        self.writer2 = None
        gc.collect()
        
    async def online_keepalive(self, Token, tok, host2, port2, key, iv, bot_uid):
        """Keep online connection alive"""
        while self.running:
            try:
                self.reader2, self.writer2 = await asyncio.open_connection(host2, int(port2))
                self.writer2.write(bytes.fromhex(tok))
                await self.writer2.drain()
                
                while self.running:
                    try:
                        data = await self.reader2.read(9999)
                        if not data:
                            break
                    except:
                        break
            except:
                await asyncio.sleep(1)
                
    async def chat_spam(self, Token, tok, host, port, key, iv, bot_uid, R):
        """Chat spammer"""
        while self.running:
            try:
                self.reader, self.writer = await asyncio.open_connection(host, int(port))
                self.writer.write(bytes.fromhex(tok))
                await self.writer.drain()
                
                # Send global message
                self.writer.write(GLobaL("fr", key, iv))
                await self.writer.drain()
                
                R.set()  # Signal ready
                
                while self.running:
                    try:
                        data = await self.reader.read(9999)
                        if not data:
                            break
                            
                        # Check for room join response
                        if data.hex().startswith("1200") and b"SecretCode" in data:
                            # Parse room info
                            U = json.loads(DeCode_PackEt(data.hex()[10:]))
                            U2 = json.loads(DeCode_PackEt(data.hex()[36:]))
                            Uu = json.loads(U["5"]["data"]["8"]["data"])
                            
                            # Get target room
                            target = int(self.target_uid)
                            sQ = Uu["SecretCode"]
                            
                            # Join room
                            self.writer.write(RedZed_3alamyia_Chat(target, sQ, key, iv))
                            await self.writer.drain()
                            
                            # Send spam message
                            spam_msg = self.create_spam_message()
                            self.writer.write(RedZed_SendMsg(spam_msg, target, bot_uid, key, iv))
                            await self.writer.drain()
                            
                            # Send invite
                            try:
                                if hasattr(self, 'writer2') and self.writer2:
                                    self.writer2.write(RedZed_SendInv(bot_uid, target, key, iv))
                                    await self.writer2.drain()
                            except:
                                pass
                            
                            # Quit room
                            try:
                                self.writer.write(quit_caht_redzed(target, key, iv))
                                await self.writer.drain()
                            except:
                                pass
                            
                            self.message_count += 1
                            print(f"[{self.uid}] Spammed {self.target_uid} - Count: {self.message_count}")
                            
                    except:
                        break
                        
            except:
                await asyncio.sleep(1)
                
    def create_spam_message(self):
        """Create spam message with formatting"""
        msg_part1 = (
            "-HELLO I AM Ax Romjan   !\n\n"
            "SUBSCRIBE ME ON YOUTUBE  OR BE BANNED \n\n"
            "SBPRIME HERE : "
        )
        msg_part2 = "@axromjanyt !! \n\n"
        msg_part3 = (
            "telegram team channel : @axemoteserver \n\n"
            "DEV Telegram username : @axromjanhissain"
        )
        
        full_msg = (
            "[FF0000][B][C]"
            + xMsGFixinG(msg_part1)
            + "[00FF00]"
            + xMsGFixinG(msg_part2)
            + "[FFFF00]"
            + xMsGFixinG(msg_part3)
        )
        
        return full_msg
        
    def get_tokens(self):
        """Get login tokens and connection info"""
        try:
            A, O = G_AccEss(self.uid, self.password)
            if not A or not O:
                return None
                
            PLaFTrom = 4
            Version, V = "2019119621", "1.120.1"
            
            # Create payload
            PyL = {
                3: str(datetime.now())[:-7],
                4: "free fire",
                5: 1,
                7: V,
                8: "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)",
                9: "Handheld",
                10: "Verizon Wireless",
                11: "WIFI",
                12: 1280,
                13: 960,
                14: "240",
                15: "x86-64 SSE3 SSE4.1 SSE4.2 AVX AVX2 | 2400 | 4",
                16: 5951,
                17: "Adreno (TM) 640",
                18: "OpenGL ES 3.0",
                19: "Google|0fc0e446-ca27-4faa-824a-d40d77767de9",
                20: "20.171.73.202",
                21: "fr",
                22: O,
                23: PLaFTrom,
                24: "Handheld",
                25: "google G011A",
                29: A,
                30: 1,
                41: "Verizon Wireless",
                42: "WIFI",
                57: "1ac4b80ecf0478a44203bf8fac6120f5",
                60: 32966,
                61: 29779,
                62: 2479,
                63: 914,
                64: 31176,
                65: 32966,
                66: 31176,
                67: 32966,
                70: 4,
                73: 2,
                74: "/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/lib/arm",
                76: 1,
                77: "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-g8eDE0T268FtFmnFZ2UpmA==/base.apk",
                78: 6,
                79: 1,
                81: "32",
                83: Version,
                86: "OpenGLES2",
                87: 255,
                88: PLaFTrom,
                89: "J\u0003FD\u0004\r_UH\u0003\u000b\u0016_\u0003D^J>\u000fWT\u0000\\=\nQ_;\u0000\r;Z\u0005a",
                90: "Phoenix",
                91: "AZ",
                92: 10214,
                93: "3rd_party",
                94: "KqsHT7gtKWkK0gY/HwmdwXIhSiz4fQldX3YjZeK86XBTthKAf1bW4Vsz6Di0S8vqr0Jc4HX3TMQ8KaUU3GeVvYzWF9I=",
                95: 111207,
                97: 1,
                98: 1,
                99: f"{PLaFTrom}",
                100: f"{PLaFTrom}",
            }
            
            # Create proto
            PyL = CrEaTe_ProTo(PyL).hex()
            Payload = bytes.fromhex(EnC_AEs(PyL))
            
            # Major login
            Response = MajorLoGin(Payload)
            if not Response:
                return None
                
            # Parse response
            BesTo_data = json.loads(DeCode_PackEt(Response))
            bot_uid = BesTo_data["1"]["data"]
            JwT_ToKen = BesTo_data["8"]["data"]
            
            # Get key and iv
            my_message = xKEys.MyMessage()
            my_message.ParseFromString(bytes.fromhex(Response))
            timestamp, key, iv = my_message.field21, my_message.field22, my_message.field23
            
            # Get ports
            url = "https://clientbp.ggwhitehawk.com/GetLoginData"
            headers = {
                "Expect": "100-continue",
                "Authorization": f"Bearer {JwT_ToKen}",
                "X-Unity-Version": "2018.4.11f1",
                "X-GA": "v1 1",
                "ReleaseVersion": "OB52",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
                "Host": "clientbp.ggwhitehawk.com",
                "Connection": "close",
                "Accept-Encoding": "gzip, deflate, br",
            }
            
            res = requests.post(url, headers=headers, data=Payload, verify=False)
            port_data = json.loads(DeCode_PackEt(res.content.hex()))
            
            address, address2 = port_data["32"]["data"], port_data["14"]["data"]
            ip, ip2 = address[:len(address)-6], address2[:len(address2)-6]
            port, port2 = address[len(address)-5:], address2[len(address2)-5:]
            
            return JwT_ToKen, key, iv, timestamp, ip, port, ip2, port2, bot_uid
            
        except Exception as e:
            print(f"Token generation error: {e}")
            return None
            
    def create_auth_token(self):
        """Create authentication token"""
        try:
            # Decode JWT
            decoded = jwt.decode(self.JwT_ToKen, options={"verify_signature": False})
            account_uid = decoded.get("account_id")
            exp_time = decoded.get("exp")
            
            # Create hex values
            encoded_account = hex(account_uid)[2:]
            hex_time = DecodE_HeX(self.Timestamp)
            
            # Create token
            jwt_hex = self.JwT_ToKen.encode().hex()
            encrypted = EnC_PacKeT(jwt_hex, self.key, self.iv)
            
            # Build final token
            length_hex = hex(len(encrypted) // 2)[2:]
            
            # Handle different account ID lengths
            padding = "00000000"
            uid_len = len(encoded_account)
            if uid_len == 9:
                padding = "0000000"
            elif uid_len == 8:
                padding = "00000000"
            elif uid_len == 10:
                padding = "000000"
            elif uid_len == 7:
                padding = "000000000"
                
            self.AutH_ToKen = f"0115{padding}{encoded_account}{hex_time}00000{length_hex}{encrypted}"
            
        except Exception as e:
            print(f"Auth token error: {e}")

def run_spammer(uid, password, target_uid, session_id):
    """Run spammer in async loop"""
    async def _run():
        spammer = FF_Spammer(uid, password, target_uid, session_id)
        with session_lock:
            active_sessions[session_id] = spammer
        result = await spammer.start_spam()
        with session_lock:
            if session_id in active_sessions:
                del active_sessions[session_id]
        return result
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()

def load_accounts(file_path="sb.json"):
    """Load accounts from sb.json"""
    import os
    
    if not os.path.isabs(file_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, file_path)
    
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            content = f.read()
            
        if not content.strip():
            return {}
        
        data = json.loads(content)
        
        if not isinstance(data, dict):
            return {}
        
        accounts = {}
        for k, v in data.items():
            uid = str(k).strip()
            pwd = str(v).strip()
            if uid and pwd:
                accounts[uid] = pwd
        
        return accounts
        
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        return {}

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        "status": "online",
        "message": "Free Fire Spam API",
        "endpoints": {
            "/spam": "POST - Start spamming",
            "/spam/<target>": "GET - Start spamming target",
            "/status/<session_id>": "GET - Check spam status",
            "/stop/<session_id>": "POST - Stop spam session",
            "/active": "GET - List active sessions",
            "/accounts": "GET - List available accounts"
        },
        "usage": {
            "post": "/spam?target=123456&duration=600",
            "get": "/spam/123456?duration=600"
        }
    })

@app.route('/spam', methods=['POST', 'GET'])
def spam_target():
    """Start spamming a target"""
    try:
        # Get target UID
        if request.method == 'POST':
            data = request.get_json()
            target_uid = data.get('target') if data else None
        else:  # GET
            target_uid = request.args.get('target')
        
        if not target_uid:
            return jsonify({
                "success": False,
                "error": "Target UID required"
            }), 400
            
        # Get duration (default 600 seconds = 10 minutes)
        try:
            duration = int(request.args.get('duration', 600))
            if duration > 3600:  # Max 1 hour
                duration = 3600
        except:
            duration = 600
            
        # Load accounts
        accounts = load_accounts()
        if not accounts:
            return jsonify({
                "success": False,
                "error": "No accounts found in sb.json"
            }), 500
            
        # Create session ID
        session_id = str(uuid.uuid4())[:8]
        
        # Start spam threads for each account
        threads = []
        results = []
        
        for uid, password in accounts.items():
            thread = threading.Thread(
                target=lambda: results.append({
                    "uid": uid,
                    "success": run_spammer(uid, password, target_uid, f"{session_id}_{uid}")
                })
            )
            thread.start()
            threads.append(thread)
            
        # Wait a bit for threads to start
        time.sleep(2)
        
        return jsonify({
            "success": True,
            "message": f"Started spamming target {target_uid}",
            "session_id": session_id,
            "target_uid": target_uid,
            "accounts_used": len(accounts),
            "duration_seconds": duration,
            "status_endpoint": f"/status/{session_id}",
            "stop_endpoint": f"/stop/{session_id}"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/spam/<target_uid>', methods=['GET'])
def spam_target_get(target_uid):
    """Start spamming target from URL path"""
    try:
        # Get duration
        try:
            duration = int(request.args.get('duration', 600))
            if duration > 3600:
                duration = 3600
        except:
            duration = 600
            
        # Load accounts
        accounts = load_accounts()
        if not accounts:
            return jsonify({
                "success": False,
                "error": "No accounts found in sb.json"
            }), 500
            
        # Create session ID
        session_id = str(uuid.uuid4())[:8]
        
        # Start spam threads
        threads = []
        results = []
        
        for uid, password in accounts.items():
            thread = threading.Thread(
                target=lambda: results.append({
                    "uid": uid,
                    "success": run_spammer(uid, password, target_uid, f"{session_id}_{uid}")
                })
            )
            thread.start()
            threads.append(thread)
            
        time.sleep(2)
        
        return jsonify({
            "success": True,
            "message": f"Started spamming target {target_uid}",
            "session_id": session_id,
            "target_uid": target_uid,
            "accounts_used": len(accounts),
            "duration_seconds": duration,
            "status_endpoint": f"/status/{session_id}",
            "stop_endpoint": f"/stop/{session_id}"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/status/<session_id>', methods=['GET'])
def check_status(session_id):
    """Check spam session status"""
    with session_lock:
        active = [sid for sid in active_sessions.keys() if sid.startswith(session_id)]
        
    return jsonify({
        "session_id": session_id,
        "active": len(active) > 0,
        "active_accounts": len(active),
        "total_accounts": len(load_accounts())
    })

@app.route('/stop/<session_id>', methods=['POST'])
def stop_spam(session_id):
    """Stop a spam session"""
    stopped = 0
    with session_lock:
        to_stop = [sid for sid in active_sessions.keys() if sid.startswith(session_id)]
        for sid in to_stop:
            try:
                active_sessions[sid].stop()
                stopped += 1
            except:
                pass
            
    return jsonify({
        "success": True,
        "message": f"Stopped {stopped} spam sessions",
        "session_id": session_id
    })

@app.route('/active', methods=['GET'])
def list_active():
    """List all active sessions"""
    with session_lock:
        sessions = {}
        for sid, spammer in active_sessions.items():
            base_id = sid.split('_')[0]
            if base_id not in sessions:
                sessions[base_id] = {
                    "accounts": []
                }
            sessions[base_id]["accounts"].append(spammer.uid)
            
    return jsonify({
        "active_sessions": len(sessions),
        "sessions": sessions
    })

@app.route('/accounts', methods=['GET'])
def list_accounts():
    """List available accounts"""
    accounts = load_accounts()
    return jsonify({
        "total": len(accounts),
        "accounts": list(accounts.keys())
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

if __name__ == "__main__":
    print(render("BLACK ADMIN X SPAM API", colors=["white", "yellow"], align="center"))
    print("\n" + "="*50)
    print("Free Fire Spam API Server")
    print("="*50)
    print("\nEndpoints:")
    print("  GET  /           - API info")
    print("  POST /spam       - Start spam (JSON: {\"target\": \"uid\"})")
    print("  GET  /spam/<uid> - Start spam target")
    print("  GET  /status/<id> - Check session status")
    print("  POST /stop/<id>   - Stop session")
    print("  GET  /active      - List active sessions")
    print("  GET  /accounts    - List available accounts")
    print("\n" + "="*50)
    print("Server starting on http://0.0.0.0:5000")
    print("="*50 + "\n")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
