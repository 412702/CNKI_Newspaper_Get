# CNKI_NewsPaper Get

通过UI自动化，抓取CNKI的报纸信息（抓取中国知网报纸数据），仅限测试和学习使用，请勿乱用

## 首先声明

代码没有经过严格的全量测试，也就是并没有完整的完成过一个抓取任务，只是写完之后，让代码自己跑了十来分钟，有结果了，就不想继续搞下去了，也不是个人必须完成的工作，只是出于兴趣随便搞搞，如果有建议想讨论的，可以邮件

![b29a8ca671813868a105a0f1706319b](https://user-images.githubusercontent.com/44056689/204200351-df62d2e6-dd3b-4d57-860f-42b86d430473.png)

## 代码说明

程序说明：此代码实现了对CNKI中报纸内容的自动化抓取，采用的是使用webdriver，模拟浏览器，自动执行，获取其中内容，由于知网的反爬较为严格，所以代码中异常识别和时间等待较多。

## 程序整体逻辑

程序总体以 python Selenium（[Selenium 浏览器自动化项目 | Selenium](https://www.selenium.dev/zh-cn/documentation/)）为依赖，使用chrome作为模拟浏览器，选择对应版本的chromedriver（[镜像位置 (npmmirror.com)](https://registry.npmmirror.com/binary.html?path=chromedriver/)），对页面dom进行分析，模拟浏览器操作，获取相应数据

## 注意：

由于CNKI有访问限制，所以只有一般对于购买了CNKI服务的高校才能实施这项操作，**同时**由于CNKI限制，需要机构账号在线的同时个人账号也要在线，所以还需要登录账号密码

# 程序结构

### 依赖

```python
# @ author： Zhang Chunli
# @ encoding: UTF-8
# @ Email: zhangchunli711@foxmail.com
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time
import random

import pandas as pd
```

### 使用

 CNKI_NewsPaper_Loader类，创建抓取任务，并开始抓取数据

```python
cnki_newpaper = CNKI_NewsPaper_Loader("智慧社区", "D:/driver/107.0/chromedriver.exe", "user_name", "user_passerword")
cnki_newpaper.startTask()
cnki_newpaper.startGraspData()
```

### 程序介绍

#### CNKI_NewsPaper_Loader类 与构造

```python
'''
description: CNKI_NewsPaper_Loader类构造，初始化基本的属性
param@ keyWord: 用于检索的关键字
param@ driver: 下载的WebDriver路径，比较常用就是chromedriver，edgedriver，firefoxdrive（比较慢）r
param@ user_name: 用于CNKI登录的个人用户用户名
param@ user_pwd: 用于CNKI登录饿个人用户密码
'''
class CNKI_NewsPaper_Loader():
    def __init__(self, keyWord, driver, user_name, user_pwd) -> None:
```

### startTask 方法(这里只展示关键代码，具体请见源代码，里面有注释,下同)

```python
# Description: 打开 driver并开始加载页面
    def startTask(self):
        # 加载
        self.browser_window = webdriver.Chrome(executable_path=self.driver)
        self.browser_window.get('https://epub.cnki.net/kns/brief/result.aspx?dbPrefix=CCND')
        self.browser_window.maximize_window()   
        self.loginTask()
```

**建立webdriver对象，打开页面，最大化窗口，然后执行登录任务（见下文）**

（下图为打开界面）
![2022-11-28-11-19-36-image](https://user-images.githubusercontent.com/44056689/204200501-61705db5-3b7c-4ac2-bb35-7371c9f3cb2d.png)

### loginTask()  loginUser()

**loginTask() 执行登录任务，当登录失败的时候则会按照时间间隔不断刷新，直到登陆成功为止** 登录成功后会记录session 的时间，因为CNKI的cookie经观察20分钟就会失效，如果大批量操作，时间会比较长，需要不定时刷新页面，以刷新cookie

```python
# 登陆 独立出来，会需要反复操作
    def loginTask(self):
        # 如果登陆失败，等待2分钟刷新页面，再次登录
        while True:
            login_status = self.loginUser()
            if login_status == 0:
                self.pageRefresh()
            elif login_status == 1: # 登陆状态，不需要输账号密码，但是需要刷一下cookie
                self.pageRefresh()
                break
            else:
                # 否则登陆成功直接结束
                break
        self.session_start_time = time.perf_counter()
```

**loginUser() 执行登录操作，对不同登录状态给予不同返回值** 首先寻找登录按钮是否存在，如果存在，就输入账号密码，如果账号密码也输入不了，就只能返回失败，后续会重新刷新进入

```python
def loginUser(self):
        try:
            login_btn = self.browser_window.find_element(By.CSS_SELECTOR, '#Ecp_top_login a')
        except Exception as e:
            try:
                self.browser_window.find_element(By.CSS_SELECTOR, '#Ecp_loginShowName')
                return 1
            except Exception as e:
                return 0
        try:
            login_btn.click()
        except Exception as e:
            return 0
        try:
            self.browser_window.find_element(By.CSS_SELECTOR, '#Ecp_TextBoxUserName').send_keys(self.__user_name)
            self.browser_window.find_element(By.CSS_SELECTOR, '#Ecp_TextBoxPwd').send_keys(self.__user_pwd)
            self.browser_window.find_element(By.CSS_SELECTOR, '#Ecp_Button1').click()
        except Exception as e:
            return 0
        return 2
```

**通过CSS选择器锁定不同dom的位置对内容进行填充和点击相关按钮，比较有好的一点是大部分dom都有ID选择器，就很好定位，比较舒服**

![2022-11-28-12-45-54-image](https://user-images.githubusercontent.com/44056689/204200565-2d0a2bf6-cdcb-45d6-9639-dbf9b0c0b039.png)

### 检索任务retrievalTask()与检索retrieval()

**retrievalTask() 会执行检索任务，对检索失败则会刷新页面，检查登录状态，之后再次检索**

```python
def retrievalTask(self):
        while True:
            if not self.retrieval():
                self.pageRefresh()
                self.loginTask()
            else:
                break
```

**retrieval() 会以构造函数的关键字进行内容检索，并将页面显示数据选择为最大**

```python
def retrieval(self):
        try:
            search_box = self.browser_window.find_element(By.CSS_SELECTOR, "#txt_1_value1")
            search_box.send_keys(self.keyWord)
            search_box.send_keys(Keys.SPACE)
            if random.random() > 0.5:
                self.browser_window.find_element(By.CSS_SELECTOR, ".search").click()
            else:
                search_box.send_keys(Keys.ENTER)
            self.browser_window.find_elements(By.CSS_SELECTOR, "#perPageDiv .sort-list li")[2].click()
            self.all_task_page = int(self.browser_window.find_element(By.CSS_SELECTOR, ".countPageMark").text.split('/')[-1])
        except Exception as e:
            return False
        return True
```

这里也是通过dom来填充与点击

### 页面列表读取任务ReaderListTask(),页面列表读取HTMLReaderList()

**ReaderListTask() 建立一个读取任务，首先，如果session超时了，刷新页面之后再操作，其次对于读取失败则进行等待后第二次读取，如果第二次还失败，那就去刷新完之后再读取**

```python
def ReaderListTask(self):
        if time.perf_counter() - self.session_start_time > 15 * 60:
            self.loginTask()
            self.retrievalTask()
            self.toTargetPage()

        read_list = self.HTMLReaderList()
        while True:
            if len(read_list) == 0:
                read_list = self.HTMLReaderList()
                if len(read_list) == 0:
                    self.pageRefresh()
                    self.loginTask()
                    self.retrievalTask()
                    self.toTargetPage()
                    read_list = self.HTMLReaderList()
                else:
                    break
            else:
                break
        return read_list
```

**获取列表则直接通过选择器得到所有HTML阅读按钮，后续则对这些按钮执行点击操作**

```python
def HTMLReaderList(self):
        try:
            return self.browser_window.find_elements(By.CSS_SELECTOR, '.operat a.icon-html')
        except Exception as e:
            return []
```

### 跳转到目标数据页toTargetPage()

**为避免抓取进度到一半直接被挂掉了，程序会记录抓取到了哪一个页面的哪一条，所以当刷新页面后就需要跳转到目标数据页**

```python
    def toTargetPage(self):
        print(f"数据页面跳转指定:{self.current_task_page}".center(50, "-"))
        if self.current_task_page == 0:
            return
        for i in range(self.current_task_page):
            self.toNextDataPage()
```

### 执行数据抓取任务 startGraspData()

**数据抓取任务 主要是对获取到的目标列表进行处理，浏览器点击列表进入新页面，获取其中tips, title, author, 正文之后，关闭页面，等待一段时间之后获取下一个**

```python
    def startGraspData(self):
        self.retrievalTask()
        data_res = []
        while True:
            read_list = self.ReaderListTask()
            while True:
                tmp_res = []
                try:
                    read_list[self.current_page_position].click()
                except Exception as e:
                    break
                self.browser_window.switch_to.window(self.browser_window.window_handles[1])
                try:
                    tmp_res.append( self.browser_window.find_element(By.CSS_SELECTOR, '.tips').text )
                    tmp_res.append(self.browser_window.find_element(By.CSS_SELECTOR, '.h1title.title').text)
                    tmp_res.append(self.browser_window.find_element(By.CSS_SELECTOR, '.author').text)
                    paraph_list = self.browser_window.find_elements(By.CSS_SELECTOR, '.p1')
                    tmp_res.append('\n'.join([item.text for item in paraph_list]))
                except Exception as e:
                    self.browser_window.close()
                    self.browser_window.switch_to.window(self.browser_window.window_handles[0])
                    break
                data_res.append(tmp_res)
                self.browser_window.close()
                self.browser_window.switch_to.window(self.browser_window.window_handles[0])
                self.current_page_position += 1
                if self.current_page_position >= 50:
                    self.current_page_position = 0
                    self.current_task_page += 1
                    # 考虑抓一页保存一次
                    pd.DataFrame(data_res, columns=['tips', 'title', 'author', 'content']).to_csv(f"./GetResult/data_res_page_{str(self.current_task_page-1)}.csv")

                    self.toNextDataPage()
                    break
                pass
            pass
            # 当任务执行到最后一页的时候，就可以break了
            if self.current_task_page >= self.all_task_page:
                break
        pass
```
