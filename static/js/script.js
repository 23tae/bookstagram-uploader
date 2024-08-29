let checkInterval = 10000; // 10초
let isLoggedIn = false;

function checkLoginStatus() {
    fetch('/login_status')
        .then(response => response.json())
        .then(data => {
            const statusText = document.getElementById('loginStatusText');
            const lastLoginTime = document.getElementById('lastLoginTime');
            const uploadButton = document.getElementById('uploadButton');

            if (data.status === 'logged_in') {
                statusText.textContent = 'Logged in';
                lastLoginTime.textContent = new Date(data.last_login).toLocaleString();
                uploadButton.disabled = false;
                
                if (!isLoggedIn) {
                    // 로그인 상태로 변경되면 확인 주기를 변경
                    checkInterval = 60000 * 60; // 60분
                    isLoggedIn = true;
                    clearInterval(statusInterval);
                    statusInterval = setInterval(checkLoginStatus, checkInterval);
                }
            } else {
                statusText.textContent = 'Logged out';
                lastLoginTime.textContent = 'N/A';
                uploadButton.disabled = true;
                
                if (isLoggedIn) {
                    // 로그아웃 상태로 변경되면 확인 주기를 변경
                    checkInterval = 10000; // 10초
                    isLoggedIn = false;
                    clearInterval(statusInterval);
                    statusInterval = setInterval(checkLoginStatus, checkInterval);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('loginStatusText').textContent = 'Error checking status';
        });
}

// 페이지 로드 시 최초 확인
checkLoginStatus();

// 로그인 상태에 따라 주기를 조절
let statusInterval = setInterval(checkLoginStatus, checkInterval);
