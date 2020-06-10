checkResultAttempt = 10
postSelectAttempt = 2
watch_interval = 1
watchGap = 0.6


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0 "

wxpay_url = "https://api.paycats.cn/v1/pay/wx/native"
alipay_url = "https://api.paycats.cn/v1/pay/alipay/f2f"
cancel_url = "https://api.paycats.cn/v1/order/close"

mch_id = 12345
secret_key = "12345"

proxy_pool_url = "12345"

### 以下内容若无必要 请勿修改
### ————————————————————

headers = {
    'User-Agent': user_agent,
    'Referer': 'http://zhjw.scu.edu.cn/student/courseSelect/courseSelect/index',
    'Host': 'zhjw.scu.edu.cn'
}

login_page_url = "http://zhjw.scu.edu.cn/login"
login_url = "http://zhjw.scu.edu.cn/login/j_spring_security_check"
query_url = "http://zhjw.scu.edu.cn/student/courseSelect/freeCourse/courseList"
planCourse_url = "http://zhjw.scu.edu.cn/student/courseSelect/planCourse/courseList"
token_url = "http://zhjw.scu.edu.cn/student/courseSelect/courseSelect/index"
postToken_url = "http://zhjw.scu.edu.cn/student/courseSelect/selectCourse/checkInputCodeAndSubmit"
captcha_url = "http://zhjw.scu.edu.cn/student/courseSelect/selectCourse/getYzmPic?time=233"
select_url = "http://zhjw.scu.edu.cn/student/courseSelect/selectCourses/waitingfor"
result_url = "http://zhjw.scu.edu.cn/student/courseSelect/selectResult/query"
courseQuery_url = "http://zhjwjs.scu.edu.cn/teacher/personalSenate/giveLessonInfo/thisSemesterClassSchedule" \
                  "/getCourseArragementPublic"


token_key = r"""<input type="hidden" id="tokenValue" value=".+"\/>"""
kcNum_key = "kcNum = \".+\""
redisKey_Key = "redisKey = \".+\""
