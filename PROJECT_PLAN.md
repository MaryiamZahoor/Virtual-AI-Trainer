# 🎯 VIRTUAL AI TRAINER - COMPREHENSIVE PROJECT PLAN

## 📋 EXECUTIVE SUMMARY

Virtual AI Trainer is a **real-time AI-powered exercise monitoring system** using YOLOv8 Pose estimation for form correction. Users get instant visual feedback (color-coded overlay) on their workout posture with angles displayed in real-time.

**Project Goal**: Help users perform exercises with correct form by analyzing their pose in real-time and providing immediate visual feedback.

---

## ✅ TECHNOLOGY STACK (APPROVED)

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Backend Language** | Python 3.11+ | ML ecosystem, MLOps tools |
| **Backend Framework** | FastAPI | Async, WebSocket support, fast, ML-friendly |
| **Pose Model** | YOLOv8 Pose | Real-time, accurate, efficient, production-ready |
| **Frontend** | HTML5/CSS/JavaScript | Client-side YOLOv8 inference using ONNX Runtime |
| **Real-time Communication** | WebSocket | Persistent connection, <100ms latency |
| **Containerization** | Docker + Docker Compose | Dev & prod consistency |
| **Cloud Platform** | AWS (ECS/Fargate + S3) | Managed containers, scalable, serverless |
| **CI/CD** | GitHub Actions | Native GitHub integration, automated testing & deployment |
| **Video Storage** | AWS S3 | Scalable, reliable storage for recordings |
| **MLOps** | MLflow + DVC | Phase 2 (model versioning & data management) |

---

## 🏗️ SYSTEM ARCHITECTURE

### High-Level Flow

```
USER PERSPECTIVE:
┌──────────────────────────────────────────────────────┐
│   Browser-based Web App                              │
│   1. Select Exercise (e.g., Squats)                  │
│   2. Webcam Permission → Video Capture               │
│   3. See Real-time Overlay:                          │
│      - Skeleton drawing with joints                  │
│      - Color-coded lines (Green/Yellow/Red)          │
│      - Angle values displayed                        │
│      - Rep counter                                   │
│   4. Complete exercise → See summary                 │
└──────────────────────────────────────────────────────┘

TECHNICAL PIPELINE (Per Frame - ~30fps):
Client Browser                     Backend (FastAPI)
├─ Webcam frame                    
├─ YOLOv8 inference (20-30ms)     
├─ Extract 17 landmarks           
├─ Calculate angles                
├─ Send via WebSocket ──────────────────> Analyze angles
│  {timestamp,                      Compare vs specs
│   landmarks,                      Generate feedback
│   angles}                    <──────── Send feedback
│                                   {correct_joints,
├─ Receive feedback                 wrong_joints,
├─ Render color overlay             suggestions}
│  (0-5ms)                         
└─ Display feedback               

REPEATED 30 TIMES PER SECOND
```

---

## 📁 PROJECT FOLDER STRUCTURE

```
virtual-trainer/
│
├── README.md                          # Project overview
├── PROJECT_PLAN.md                    # This file
├── docker-compose.yml                 # Local dev setup
├── .env.example                       # Environment template
├── .gitignore
│
├── .github/
│   └── workflows/
│       ├── ci-test.yml                # Run tests on PR
│       └── deploy-aws.yml             # Deploy to AWS on merge to main
│
├── backend/                           # FastAPI Application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app & WebSocket setup
│   │   ├── config.py                  # Config, environment variables
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py              # REST endpoints (/health, /exercises, etc)
│   │   │   └── websocket.py           # WebSocket handlers for real-time feedback
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── exercises.py           # Exercise data models & schemas
│   │   │   ├── pose.py                # Pose/landmark models
│   │   │   └── feedback.py            # Feedback response schemas
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── angle_analyzer.py      # Core angle calculation (MATH)
│   │   │   ├── feedback_engine.py     # Generate human-readable feedback
│   │   │   ├── exercise_validator.py  # Validate pose against specs
│   │   │   └── session_manager.py     # Session tracking
│   │   │
│   │   ├── ml/
│   │   │   ├── __init__.py
│   │   │   ├── exercise_definitions.py # Hard-coded angle specs for each exercise
│   │   │   ├── pose_constants.py      # Keypoint indices & names
│   │   │   └── pose_utils.py          # Pose processing utilities
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py              # Logging setup
│   │       └── constants.py           # App-wide constants
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_angle_analyzer.py     # Unit tests for angles
│   │   ├── test_feedback_engine.py    # Unit tests for feedback
│   │   └── test_websocket.py          # WebSocket connection tests
│   │
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Container image
│   ├── .dockerignore
│   └── pytest.ini                     # pytest configuration
│
├── frontend/                          # Web Frontend
│   ├── index.html                     # Main HTML
│   ├── style.css                      # Styling
│   ├── config.js                      # Frontend config
│   │
│   ├── js/
│   │   ├── app.js                     # Main application controller
│   │   ├── pose-detector.js           # YOLOv8 model loading & inference
│   │   ├── canvas-renderer.js         # Skeleton drawing & color overlay
│   │   ├── websocket-client.js        # WebSocket connection & messaging
│   │   ├── exercise-selector.js       # Exercise UI management
│   │   ├── feedback-renderer.js       # Feedback display logic
│   │   └── utils.js                   # Helper utilities
│   │
│   ├── models/
│   │   └── yolov8n-pose.onnx          # YOLOv8 Nano Pose model (~6MB)
│   │
│   ├── assets/
│   │   ├── exercise-references/       # Reference images for each exercise
│   │   │   ├── squats.png
│   │   │   ├── pushups.png
│   │   │   └── ... more exercises
│   │   └── icons/
│   │
│   ├── Dockerfile                     # Serve static files with Nginx
│   └── nginx.conf                     # Nginx configuration
│
├── docs/
│   ├── api-documentation.md           # API endpoints & WebSocket messages
│   ├── architecture.md                # Detailed architecture decisions
│   ├── exercise-specifications.md     # Angle specs for each exercise
│   ├── deployment-guide.md            # AWS deployment steps
│   ├── development-setup.md           # Local dev setup
│   └── mlops-roadmap.md               # MLflow/DVC integration plan
│
└── .env.example                       # Example environment file
```

---

## 🎯 PHASE 1: MVP (Weeks 1-2)

### ✅ Features to Build

#### Backend (FastAPI)
1. **REST API Endpoints**
   - `GET /health` → Server status
   - `GET /exercises` → List all exercises with angle specs
   - `GET /exercises/{id}` → Single exercise details

2. **WebSocket Endpoint**
   - `WS /ws/analyze` → Real-time pose analysis
   - **Receive**: `{landmarks: [x,y,confidence]×17, timestamp, exercise_id}`
   - **Send**: `{feedback: {correct_joints, wrong_joints}, suggestions, accuracy_score}`

3. **Core Logic: Angle Analysis Engine** (`services/angle_analyzer.py`)
   - Calculate angles between 3 points (joint1 → joint2 → joint3)
   - Example: Knee angle = angle(hip, knee, ankle)
   - Return: angle value in degrees

4. **Exercise Validation** (`services/exercise_validator.py`)
   - Compare calculated angles vs target specs
   - Classify each joint as: ✅ Correct | ⚠️ Warning | ❌ Incorrect
   - Generate suggestions ("Bend your knee more", "Stand straighter")

5. **Pre-defined Exercises** (`ml/exercise_definitions.py`)
   ```python
   {
       "squats": {
           "angles": {
               "left_knee": {"min": 80, "max": 100, "target": 90},
               "right_knee": {"min": 80, "max": 100, "target": 90},
               "left_hip": {"min": 70, "max": 90, "target": 80},
               "right_hip": {"min": 70, "max": 90, "target": 80}
           },
           "start_pose": "standing_upright",
           "end_pose": "full_squat"
       },
       // ... more exercises
   }
   ```

#### Frontend (HTML/CSS/JS)
1. **UI Components**
   - Exercise selector dropdown
   - Start/Stop buttons
   - Rep counter display
   - Angle readout display

2. **Canvas Rendering** (`canvas-renderer.js`)
   - Draw 17 keypoints as circles
   - Draw 25 bones (connections between keypoints)
   - **Color Logic**:
     - 🟢 **Green**: Angle within target ± tolerance
     - 🟡 **Yellow**: Angle in warning zone (10% deviation)
     - 🔴 **Red**: Angle outside acceptable range

3. **Pose Detection** (`pose-detector.js`)
   - Load YOLOv8 Pose model (ONNX Runtime in browser)
   - Process webcam frames at ~30fps
   - Extract 17 landmarks (keypoints)
   - Handle GPU/CPU fallback

4. **WebSocket Communication** (`websocket-client.js`)
   - Connect to `ws://backend:8000/ws/analyze`
   - Send landmarks every frame
   - Receive feedback & render immediately

5. **Exercises Supported (MVP)**
   - ✅ **Squats** - Knee & hip angles
   - ✅ **Push-ups** - Elbow & shoulder alignment
   - ✅ **Lunges** - Front knee, back knee angles
   - ✅ **Shoulder Press** - Elbow angle, back straightness
   - ✅ **Plank** - Body alignment

### 📦 Deliverables
- ✅ Fully functional FastAPI backend with WebSocket support
- ✅ HTML/CSS/JS frontend with YOLOv8 integration
- ✅ Docker Compose setup (backend + frontend)
- ✅ Basic GitHub Actions CI (tests pass before merge)
- ✅ Documented API & architecture

---

## 🚀 PHASE 2: AWS DEPLOYMENT (Weeks 3-4)

### 🏭 AWS Infrastructure Setup

```
┌─────────────────────────────────────────────────────────┐
│ AWS Account Setup                                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ECR (Elastic Container Registry)                      │
│  ├─ backend:latest                                     │
│  └─ frontend:latest                                    │
│                                                         │
│  ECS Cluster (Fargate Launch Type)                     │
│  ├─ Backend Service                                    │
│  │  ├─ Task Definition: 2 vCPU, 4GB RAM               │
│  │  ├─ Desired Count: 2-4 tasks (auto-scaling)        │
│  │  └─ Service discovery for WebSocket                │
│  │                                                     │
│  ├─ Frontend Service                                   │
│  │  ├─ Task Definition: 0.5 vCPU, 1GB RAM            │
│  │  └─ Desired Count: 2 tasks (CDN + LB)              │
│                                                         │
│  ALB (Application Load Balancer)                       │
│  ├─ HTTP/HTTPS listener (auto redirect)               │
│  ├─ Target Group: ECS tasks                           │
│  ├─ Health checks every 30s                           │
│  └─ WebSocket routing support                         │
│                                                         │
│  S3 Buckets                                            │
│  ├─ exercise-videos/ (user recordings)                │
│  ├─ reference-media/ (exercise images)                │
│  └─ model-artifacts/ (YOLOv8 models)                  │
│                                                         │
│  RDS PostgreSQL (t3.micro, optional Phase 2)          │
│  ├─ Sessions table                                    │
│  ├─ User profiles                                     │
│  └─ Exercise metrics                                  │
│                                                         │
│  CloudWatch                                            │
│  ├─ Logs from ECS tasks                               │
│  ├─ Performance metrics (CPU, memory)                 │
│  └─ Alarms for auto-scaling                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 📋 AWS Setup Checklist
- [ ] Create IAM roles & policies
- [ ] Create ECR repositories
- [ ] Create ECS cluster & service
- [ ] Configure ALB & target groups
- [ ] Create S3 buckets with proper access
- [ ] Set up CloudWatch logging
- [ ] Configure auto-scaling policies
- [ ] Set up Route53 DNS (optional)
- [ ] Create RDS instance (if needed)

### 🔄 CI/CD Pipeline (GitHub Actions)

**Trigger**: Push to `main` branch

```yaml
# File: .github/workflows/deploy-aws.yml

on:
  push:
    branches: [main]

jobs:
  test:
    - Run pytest for backend
    - Run linting (flake8)
    - Check bundle size (frontend)
    
  build:
    - Build backend Docker image
    - Push to ECR
    - Build frontend Docker image
    - Push to ECR
    
  deploy:
    - Update ECS task definitions
    - Deploy to Fargate
    - Run smoke tests
    - Notify on Slack
```

### 📦 AWS Deployment Deliverables
- ✅ Docker images in ECR
- ✅ ECS services running on Fargate
- ✅ ALB routing traffic correctly
- ✅ S3 buckets for storage
- ✅ CloudWatch monitoring & logs
- ✅ GitHub Actions CD pipeline
- ✅ Domain name (Route53)

---

## 🔧 PHASE 2 ENHANCEMENTS (Optional)

### Database Integration
- User authentication & profiles
- Session history & statistics
- Exercise performance trends

### MLOps Integration
- MLflow for model experiment tracking
- DVC for data versioning
- Custom YOLOv8 fine-tuning pipeline
- Model registry & versioning

### Features
- User login/sign-up
- Session replay & analytics
- Multi-language support
- Mobile app (React Native)

---

## 🌐 DEPLOYMENT ARCHITECTURE

### Local Development (Phase 1)
```bash
docker-compose up
# Runs:
# - Backend on http://localhost:8000
# - Frontend on http://localhost:3000
# - FastAPI docs on http://localhost:8000/docs
```

### AWS Production (Phase 2)
```
Domain: trainer.example.com (Route53)
   ↓
CloudFront CDN (optional, for static files)
   ↓
Application Load Balancer (ALB)
   ↓
ECS Services (Fargate)
   ├─ Backend: 4 tasks × (2 vCPU, 4GB RAM)
   └─ Frontend: 2 tasks × (0.5 vCPU, 1GB RAM)
   ↓
S3 (video storage) + RDS (database)
```

---

## 📊 ESTIMATED RESOURCES & COSTS (Phase 2)

### AWS Monthly Cost Breakdown
| Service | Configuration | Cost/Month |
|---------|---------------|-----------|
| **ECS/Fargate** | 4 tasks (2 vCPU, 4GB) + 2 tasks (0.5 vCPU, 1GB) | $60 |
| **ALB** | Standard load balancer | $20 |
| **S3** | 1TB storage + data transfer | $25 |
| **RDS** | t3.micro PostgreSQL, single AZ | $35 |
| **NAT Gateway** | Data processing | $35 |
| **CloudWatch** | Logs & monitoring | $10 |
| **Route53** | Domain hosting (optional) | $0.50 |
| **Total Estimate** | | **$185/month** |

---

## 🎓 EXERCISE ANGLE SPECIFICATIONS (Phase 1)

### 1. Squats
```
Target Angles:
- Left Knee: 90° ± 10° (range: 80-100°)
- Right Knee: 90° ± 10° (range: 80-100°)
- Left Hip: 80° ± 10° (range: 70-90°)
- Right Hip: 80° ± 10° (range: 70-90°)

Reference Pose:
- Start: Standing upright, feet shoulder-width apart
- End: Thighs parallel to ground
```

### 2. Push-ups
```
Target Angles:
- Left Elbow: 90° ± 15° (range: 75-105°)
- Right Elbow: 90° ± 15° (range: 75-105°)
- Body Alignment: Straight line from head to heels

Reference Pose:
- Start: Plank position
- End: Chest near ground
```

### 3. Lunges
```
Target Angles:
- Front Left Knee: 90° ± 10° (range: 80-100°)
- Back Right Knee: 60° ± 10° (range: 50-70°)
- Torso: Upright (90° with ground)

Reference Pose:
- Start: Standing, feet together
- End: Front leg bent 90°, back knee near ground
```

### 4. Shoulder Press
```
Target Angles:
- Left Elbow: 80° ± 10° (range: 70-90°)
- Right Elbow: 80° ± 10° (range: 70-90°)
- Back: Straight (neutral spine)

Reference Pose:
- Start: Dumbbells at shoulder height
- End: Arms fully extended overhead
```

### 5. Plank
```
Target Angles:
- Body Alignment: Straight line from head to heels
- Elbow Angle: 90° ± 5° (range: 85-95°)

Reference Pose:
- Position: Forearms on ground, elbows under shoulders
- Duration: 30-60 seconds
```

---

## 🔐 PHASE 1 CONSTRAINTS & DECISIONS

### What's NOT Included in Phase 1
- ❌ User database/authentication
- ❌ Session recording to S3
- ❌ Text-to-Speech narration
- ❌ Mobile app
- ❌ Advanced analytics dashboard
- ❌ Custom exercise builder
- ❌ MLflow/DVC integration

### Why These Decisions?
1. **MVP First**: Launch core feature (real-time feedback) quickly
2. **Simplify**: Focus on accuracy of angle detection
3. **Iterate**: Get user feedback before adding complexity
4. **Cost**: Reduce initial AWS costs
5. **Time**: Deliver Phase 1 in 2 weeks

---

## 🔄 DEVELOPMENT WORKFLOW

### Day 1-2: Backend Setup
- [ ] FastAPI app structure
- [ ] WebSocket handler
- [ ] Angle calculation engine
- [ ] Exercise definitions

### Day 3-4: Frontend Setup
- [ ] HTML/CSS UI
- [ ] YOLOv8 model integration
- [ ] Canvas rendering
- [ ] WebSocket client

### Day 5: Integration & Testing
- [ ] End-to-end testing (browser → backend → feedback)
- [ ] Load testing (30fps × 60 seconds)
- [ ] Edge cases (lost connection, model errors)

### Day 6: Docker & Deployment Prep
- [ ] Dockerize backend & frontend
- [ ] docker-compose.yml
- [ ] GitHub Actions CI
- [ ] Documentation

### Day 7-8: AWS Deployment (Phase 2)
- [ ] ECR setup
- [ ] ECS service creation
- [ ] ALB configuration
- [ ] CD pipeline

---

## 📝 KEYPOINT INDICES (YOLOv8 Pose - 17 Points)

```
0: nose
1: left_eye
2: right_eye
3: left_ear
4: right_ear
5: left_shoulder
6: right_shoulder
7: left_elbow
8: right_elbow
9: left_wrist
10: right_wrist
11: left_hip
12: right_hip
13: left_knee
14: right_knee
15: left_ankle
16: right_ankle
```

---

## 🎯 SUCCESS CRITERIA

### Phase 1 (MVP)
- ✅ Achieves <100ms feedback latency
- ✅ Correctly detects pose 90%+ accuracy
- ✅ Smooth 30fps overlay rendering
- ✅ Handles 5+ concurrent users locally
- ✅ All exercises have accurate angle detection

### Phase 2 (AWS)
- ✅ Scales to 100+ concurrent users
- ✅ <50ms feedback latency (network included)
- ✅ 99.9% uptime
- ✅ Automated CI/CD pipeline
- ✅ Cost-optimized AWS deployment

---

## 📚 RESOURCES & DOCUMENTATION

- **YOLOv8 Docs**: https://docs.ultralytics.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **ONNX Runtime JS**: https://onnxruntime.ai/docs/
- **WebSocket Guide**: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- **AWS ECS**: https://aws.amazon.com/ecs/
- **GitHub Actions**: https://docs.github.com/en/actions

---

## 🤝 TEAM COLLABORATION

### Code Organization
- Backend team: `backend/` folder
- Frontend team: `frontend/` folder
- Separate branches for features
- PRs require code review

### Communication
- API contract agreed upfront (WebSocket message format)
- Weekly syncs on progress
- Slack for quick questions

---

## ✅ APPROVAL CHECKLIST

**Before starting development, confirm:**
- [ ] Architecture approved
- [ ] Tech stack confirmed
- [ ] Phase 1 scope locked
- [ ] AWS strategy understood
- [ ] Exercise specs validated
- [ ] Team assignments clear
- [ ] Development timeline agreed

---

## 📞 NEXT STEPS

1. **Finalize Project Plan** ← You are here
2. **Set up Local Development Environment**
   - Create backend structure
   - Create frontend structure
   - Initialize git repository
   - Create docker-compose.yml

3. **Implement Phase 1 Backend**
   - FastAPI app setup
   - Angle analyzer
   - WebSocket handler

4. **Implement Phase 1 Frontend**
   - YOLOv8 integration
   - Canvas rendering
   - WebSocket client

5. **Test & Debug**
   - Unit tests
   - Integration tests
   - Manual testing

6. **Deploy Phase 2**
   - AWS setup
   - CI/CD pipeline
   - Production deployment

---

**Last Updated**: May 20, 2026
**Status**: ✅ APPROVED
**Next Review**: After Phase 1 completion

