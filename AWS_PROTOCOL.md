# 🚁 AWS PROTOCOL

> Quick handshake for AWS infrastructure readiness

---

## 📖 Protocol Definition

**"Roll with AWS"** = AWS EC2 instance is deployed, configured, and ready

**When you say:** "Roll with AWS"

**What I understand:**
- ✅ AWS EC2 instance is running
- ✅ Instance is accessible (SSH working)
- ✅ No further setup needed
- ✅ Ready for MACV SOG deployment
- ✅ Security groups configured
- ✅ Storage provisioned

**My response:** Proceed directly to MACV SOG deployment commands

---

## 🔗 Common AWS Protocol Phrases

| Phrase | Meaning | Response |
|--------|---------|----------|
| **"Roll with AWS"** | Instance ready, deploy MACV SOG | ✅ Proceed with deployment |
| **"AWS UP"** | Instance running, check status | Get logs/metrics |
| **"AWS DOWN"** | Instance stopped/offline | Spin up or diagnose |
| **"AWS READY"** | Same as "Roll with AWS" | Deploy MACV SOG |
| **"AWS RESET"** | Clear instance, fresh deploy | Wipe and redeploy |

---

## 🎯 Standard AWS Handshake

```
You: "Roll with AWS"
Me: ✅ UNDERSTOOD - AWS EC2 READY
    → Proceeding with MACV SOG deployment
    → Instance IP: [XXX.XXX.XXX.XXX]
    → Status: ARMED for recon pipeline
```

---

## 🚀 When You Say "Roll with AWS" I Will:

1. **Assume instance is live** (no connectivity checks)
2. **Skip setup verification** (go straight to deployment)
3. **Execute MACV SOG deploy** on your instance
4. **Provide deployment status**
5. **Confirm MACV SOG ARMED**

---

## 📝 AWS Instance Checklist (For You)

Before saying "Roll with AWS", verify:

- [ ] AWS EC2 instance is running (t3.large+ recommended)
- [ ] Ubuntu 22.04 LTS installed
- [ ] SSH key configured and accessible
- [ ] Security group allows SSH from your IP
- [ ] EBS storage provisioned (100GB+)
- [ ] Instance has public IP or VPN access
- [ ] Can SSH into instance successfully

---

## 🔐 AWS Protocol Security

When you provide instance IP/credentials:
- Keep SSH keys private
- Only provide access to me in this session
- Rotate credentials after deployment
- Restrict security group to your IP only

---

## 🎯 Full Deployment Flow

```
Step 1: You say "Roll with AWS"
Step 2: I acknowledge AWS ready
Step 3: I execute MACV SOG deploy
Step 4: MACV SOG ARMED confirmation
Step 5: Monitoring begins
```

---

## 🚨 AWS Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| `AWS READY` | Instance online | Deploy MACV SOG |
| `AWS HOT` | Instance running, MACV SOG active | Monitor findings |
| `AWS COLD` | Instance offline | Restart |
| `AWS ERROR` | Instance error/unreachable | Troubleshoot |
| `AWS RESET` | Wipe and redeploy | Full refresh |

---

## 🐺 Protocol Lock-In

**From now on:**

```
You: "Roll with AWS"
Me: "AWS PROTOCOL CONFIRMED - Standing by for MACV SOG deployment"
```

No questions asked. Direct to deployment. 🚀

---

*AWS Protocol Established. Ready to roll.* 🚁
