# 📘 acsm-convert

A lightweight web tool to **download and remove DRM** from `.acsm` files using [libgourou](https://github.com/bcliang/docker-libgourou) and Docker Compose.

```bash
git clone https://github.com/roosmsg/acsm-convert.git
cd acsm-convert
docker compose up --build
```

After deploying, open the app in your browser:  
  
  http://localhost:5070
<br />
<br />
    
---

### 🔐 Adobe ID Activation (One-Time Setup)

To use `libgourou`, you must **activate your Adobe ID** inside the container once. This generates the necessary DRM keys.

#### 🔧 Step 1: Find the Container Name and Go to it

```bash
docker ps
docker exec -it <container-name> /bin/sh
```
#### 🔑 Step 2: Run the Activation Commander

Inside the container, run:

```bash
adept_activate -u your_email@adobe.com -p your_password -O /home/libgourou/.adept
```
This command connects to Adobe’s servers and generates your activation credentials.

#### 📂 Step 3: Verify the Activation Files

Check the output directory:

```bash
ls -l /home/libgourou/.adept
```


You should see:

activation.xml  
device.xml  
devicesalt

📦 These files are your personal ADEPT device credentials.  
🔒 Back them up so you can reuse them later without reactivating.
