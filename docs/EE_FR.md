# Email Essence - Functional Requirements Specification
Broken down by development checkpoint

#### TODO
review acceptance criteria
add deployment specification/requirements

## MVP
`Completion → February 17th 2025; ahead of MidQ Presentation`

`Full test coverage→ March 21st 2025; ahead of FinalQ Presentation`

### FR01 - Email Retrieval System
- [ ] **Status**: Completed, pending update to query parameters

**Owner**: Joseph , Ritesh
- System must implement secure email retrieval using Gmail API/IMAP
- OAuth 2.0 authentication required for secure access
- Includes database integration (MongoDB) for email storage
- Redis caching implementation for performance optimization

**User Story**: As a user, I want to securely connect my Gmail or other email account so that I can view my emails in the application.

**Acceptance Criteria**: The system retrieves emails after the user authorizes access via OAuth 2.0 and displays them in the inbox view.

#### Sub-requirements:
- [x] FR01.1 - Database Setup (MongoDB) - **Completed** (Ritesh)
- [ ] FR01.2 - Database Integration - **In Progress** (Ritesh)

### FR02 - AI-Powered Email Summarization
- [ ] **Status**: Completed, pending other model integrations

**Owner**: Joseph
- Automatic generation of concise email summaries (1-2 sentences) and key topics
- Integration with LLM for high-quality summarization
- Summaries displayed in inbox list view
- Current implementation uses OpenAI with an abstraction layer in place to support other models including a local model

**User Story**: As a user I want my emails summarized using AI, so that I can quickly understand important information without needing to read the full email.

**Acceptance Criteria**: 
- Upon fetching an email, the system uses the integrated AI model to generate a concise summary
- Summaries are displayed in the inbox list view with key points visible at a glance

### FR03 - Minimal Web Interface
- [ ] **Status**: In Progress

**Owner**: Shayan, Emma
- Implementation of core UI components and layout
- React-based frontend architecture

**User Story**: As a user, I want to see an overview of my inbox and manage my preferences so that I can efficiently handle my emails.

#### Dashboard (FR03.1):
- [ ] FR03.1.1 - Email List - **In Progress**
- [ ] FR03.1.2 - Miniview - **In Progress**

**Acceptance Criteria**: The dashboard displays a list of emails with sender information and timestamps.

#### Inbox View (FR03.2):
- [ ] FR03.2.1 - Email Entry Component - **In Progress**
- [ ] FR03.2.2 - Inbox Box - **In Progress**
- [ ] FR03.2.3 - Email Component - **In Progress**
- [ ] FR03.2.4 - Reader View - **In Progress**

**Acceptance Criteria**: The system displays emails in a simplified format when opened, removing extraneous formatting.

#### Navigation (FR03.3):
- [ ] FR03.3.1 - Logo Button - **In Progress**
- [ ] FR03.3.2 - Inbox Button - **In Progress**
- [ ] FR03.3.3 - Settings Button - **In Progress**

#### Settings Interface (FR03.4):
- [ ] FR03.4.1 - Summaries Toggle - **In Progress**
- [ ] FR03.4.2 - Email Fetch Interval - **In Progress**
- [ ] FR03.4.3 - Theme Selector - **In Progress**

**Acceptance Criteria**: Users can modify preferences including email fetch frequency, ?summary generation settings, and ?theme through the settings interface.

### FR06 - OAuth 2.0 Authentication
- [ ] **Status**: Completed (Part of FR01) pending integration with user management

**Owner**: Joseph
- Secure integration with external email services
- Protection of user credentials
- Standardized authentication flow

**User Story**: As a user, I want to connect my email account securely without exposing my login credentials.

**Acceptance Criteria**: The system uses OAuth 2.0 to authenticate users and access their email data securely.

## Post-MVP Requirements
`Completion → ?June 7th 2025?; ahead of MidQ Presentation`

`Full test coverage→ ?June 14th 2025?; ahead of FinalQ Presentation`
### FR01.3 -> 1.4 Email/Summary Caching
- [ ] **Status**: In Progress

**Owner**: Ritesh, Joseph
- Redis caching implementation for performance optimization

#### Sub-requirements:
- FR01.3 - Caching Setup (Redis) - **Not Started**
- FR01.4 - Caching Integration - **Not Started**


### FR04 - Extended Web Interface
**Status**: Not Started

**Owner**: Shayan, Emma
- More dynamic, modular dashboard
- Customizable inbox views
- Advanced user settings and preferences
- Weighted Email List (FR05)

**User Story**: As a user, I want to customize my dashboard view by organizing emails based on importance, categories, or tags.

**Acceptance Criteria**: 
- Users can rearrange and customize dashboard elements
- Users can modify UI settings, including layout, themes, and notification preferences

### FR05 - Keyword Analysis
**Status**: Not Started

**Owner**:  Ritesh / Joseph
- Implementation of NLP-based keyword extraction
- Highlight key phrases and topics within emails
- Integration with summary generation system

**User Story**: As a user, I want my emails to be analyzed so that important keywords or topics are highlighted.

**Acceptance Criteria**: The system identifies and highlights important keywords within the email summary or reader view.

### FR07 - Cross-Platform Desktop Support
**Status**: Not Started

**Owner**: Shayan, Emma
- Tauri-based desktop application development
- Ensure feature parity with web version
- Cross-platform compatibility (Windows, macOS, Linux)

**User Story**: As a user, I want to access my emails via both the web and desktop application with a consistent experience.

**Acceptance Criteria**: The web and desktop versions of the app offer a unified experience, with consistent features across platforms.

## Testing Status
- No test results available for any components
- Test implementation is in progress for React components
- Backend testing framework is being established
#### Frontend Testing Coverage
|Classification | Test Coverage |
|-------|---------------|

#### Backend Testing Coverage
|Module | Test Coverage |
|-------|---------------|
|Email Routes | 0% |
|Summary Routes | 0% |
|Auth Routes | 0% |
|User Routes | 0% |
|Email Service | 0% |
|Summary Service | 0% |
|Auth Service | 0% |
|User Service | 0% |


## Notes
- All frontend components are individually tested
- Backend components require persistent storage implementation
- Initial deployment will focus on web interface before desktop support
- Local LLM implementation is being explored as an alternative to paid APIs