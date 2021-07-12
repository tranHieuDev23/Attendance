## Installation guide
**1. Install docker  **
**2. Pull code and build  **
git clone https://github.com/tranHieuDev23/Attendance.git  
docker build . -t attendance  
**3. Deploy docker  **
docker run -d -p 8000:8000 attendance  
**4. Open browser and run** localhost:8000
