# @ author： Zhang Chunli
# @ encoding: UTF-8
# @ Email: zhangchunli711@foxmail.com
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time
import random

import pandas as pd

class CNKI_NewsPaper_Loader():

    # 构造
    def __init__(self, keyWord, driver, user_name, user_pwd) -> None:
        self.keyWord = keyWord
        self.driver = driver

        self.browser_window = 0
        # 用户账号密码
        self.__user_name = user_name
        self.__user_pwd = user_pwd

        # 当前 已经抓取到的页面
        self.current_task_page = 0
        self.all_task_page = 0

        # 当前页面已经抓取到的第几个
        self.current_page_position = 0
        # session 开始时间
        self.session_start_time = time.perf_counter()

    # Description: 打开 driver并开始加载页面
    def startTask(self):
        # 加载
        self.browser_window = webdriver.Chrome(executable_path=self.driver)
        time.sleep(1.5)
        self.browser_window.get('https://epub.cnki.net/kns/brief/result.aspx?dbPrefix=CCND')
        time.sleep(1.5)
        self.browser_window.maximize_window()   
        # 登录操作
        time.sleep(1.5)
        self.loginTask()
    
    # 开始抓取任务
    def startGraspData(self):
        # 检索
        self.retrievalTask()
        
        # res = pd.DataFrame(0, columns=['tips', 'title', 'author', 'content'])
        # 开始对数据抓取
        time.sleep(2.5)
        data_res = []
        while True:
            print("开始获取数据")
            # 获取当前页面 的列表
            read_list = self.ReaderListTask()
            time.sleep(2 + random.random()*5)

            # 遍历read_list开始获取数据
            # self.current_page_position
            while True:
                tmp_res = []
                # 点击进入 HTML阅读界面
                print("打开页面, 5-10 s 后开始抓取")
                try:
                    read_list[self.current_page_position].click()
                except Exception as e:
                    # 打开页面出问题, 这里一般不会出问题, 出了问题就直接break吧, 然后这一页重新进行, 也就是对当前页面-1, 因为后面会有 +1
                    print(f"打开页面出问题, 这里一般不会出问题, 出了问题就直接break吧:{e}")

                    break
                time.sleep(5 + random.random()*5)
                # 弹出新的页面，进行页面切换与数据获取
                self.browser_window.switch_to.window(self.browser_window.window_handles[1])
                try:
                    # 报纸 时间
                    tmp_res.append( self.browser_window.find_element(By.CSS_SELECTOR, '.tips').text )
                    # 标题
                    tmp_res.append(self.browser_window.find_element(By.CSS_SELECTOR, '.h1title.title').text)
                    # 作者
                    tmp_res.append(self.browser_window.find_element(By.CSS_SELECTOR, '.author').text)
                    # 得到列表之后直接遍历就可以获取到全文内容, 全文内容列表

                    paraph_list = self.browser_window.find_elements(By.CSS_SELECTOR, '.p1')
                    tmp_res.append('\n'.join([item.text for item in paraph_list]))
                    time.sleep(10+random.random()*10)
                except Exception as e:
                    # 这个如果报错，那就是页面出了问题
                    # 关闭页面，并将焦点还给上一页
                    self.browser_window.close()
                    self.browser_window.switch_to.window(self.browser_window.window_handles[0])
                    # 多等一会儿
                    r_time = 60 + 60*random.random()
                    print("正文数据获取出错, 将重新获取列表后,再次继续抓取")
                    print(f"下一次执行在{str(r_time)}之后")
                    time.sleep(r_time)
                    break

                print(tmp_res)
                
                data_res.append(tmp_res)
                 
                # 关闭页面，并将焦点换给上一页
                self.browser_window.close()
                self.browser_window.switch_to.window(self.browser_window.window_handles[0])

                # 进行下一条, 两条的时间间隔为 [60,120)s
                self.current_page_position += 1
                r_time = 60 + 60*random.random()
                print(f"正在获取正文,下一次执行在  {str(r_time)}  之后".center(100, "*"))
                time.sleep(r_time)

                # 这一页收完之后，重置当前页面位置索引, 转到下一页
                if self.current_page_position >= 50:
                    self.current_page_position = 0
                    self.current_task_page += 1
                    # 考虑抓3页保存一次，如果已经抓3页了，那么就先暂时保存一下
                    # if self.current_task_page % 3 == 0:
                    #     n = self.current_task_page
                    #     pd.DataFrame(data_res, columns=['tips', 'title', 'author', 'content']).to_csv(f"./GetResult/data_res_{str(n-3)}_{str(n-1)}.csv")

                    # 考虑抓一页保存一次
                    pd.DataFrame(data_res, columns=['tips', 'title', 'author', 'content']).to_csv(f"./GetResult/data_res_page_{str(self.current_task_page-1)}.csv")
                    
                    # 下一页数据
                    self.toNextDataPage()
                    break
                pass
            pass
            # 当任务执行到最后一页的时候，就可以break了
            if self.current_task_page >= self.all_task_page:
                print("所有数据抓取完毕，检查抓取结果".center(60, "-"))
                break
        pass

    # 下一个数据页
    def toNextDataPage(self):
        print(f"下一页数据！".center(50, "-"))

        # 两个按钮随机按
        if random.random() >= 0.5:
            self.browser_window.find_element(By.CSS_SELECTOR, '#Page_next_top').click()  # 顶部下一页图标
        else:
            self.browser_window.find_element(By.CSS_SELECTOR, '#PageNext').click()
    # 跳到需要抓数据的节面
    def toTargetPage(self):
        print(f"数据页面跳转指定:{self.current_task_page}".center(50, "-"))
        if self.current_task_page == 0:
            return
        
        if self.current_task_page > self.all_task_page:
            print("出了不得了得错误")
            return
        
        for i in range(self.current_task_page):
            self.toNextDataPage()
            time.sleep(2 + random.random() * 5)

    # 登陆 独立出来，可能会需要反复操作
    def loginTask(self):
        print(f"登陆状态检查：{self.__user_name}".center(50, "-"))
        time.sleep(1.5)
        # 如果登陆失败，等待2分钟刷新页面，再次登录
        while True:
            login_status = self.loginUser()
            if login_status == 0:
                print("登陆失败，等待下次登录 30后重试".center(30, "-"))
                time.sleep(30)
                self.pageRefresh()
            elif login_status == 1: # 登陆状态，不需要输账号密码，但是需要刷一下cookie
                self.pageRefresh()
                break
            else:
                # 否则登陆成功直接结束
                break
        self.session_start_time = time.perf_counter()
        time.sleep(2)

    def loginUser(self):
        time.sleep(1.5)
        # 登陆按钮
        try:
            login_btn = self.browser_window.find_element(By.CSS_SELECTOR, '#Ecp_top_login a')
        except Exception as e:
            # 登陆按钮不存在，即处于已登陆状态 或 报错状态
            try:
                # 处于登陆状态
                self.browser_window.find_element(By.CSS_SELECTOR, '#Ecp_loginShowName')
                return 1
            except Exception as e:
                # 如果是在这里，那么就处于报错状态，需要刷新节面
                
                # self.pageRefresh()
                return 0

        #  点击登录，弹出登录窗口，输入账号密码，点击登录按钮
        try:
            login_btn.click()
            time.sleep(1.5)
        except Exception as e:
            print("弹出登录页面失败")
            return 0
        
        try:
            # 给0.5s 以给浏览器页面响应
            time.sleep(0.5)
            self.browser_window.find_element(By.CSS_SELECTOR, '#Ecp_TextBoxUserName').send_keys(self.__user_name)
            time.sleep(1.5)
            self.browser_window.find_element(By.CSS_SELECTOR, '#Ecp_TextBoxPwd').send_keys(self.__user_pwd)
            time.sleep(1.5)
            self.browser_window.find_element(By.CSS_SELECTOR, '#Ecp_Button1').click()
        except Exception as e:
            print("登录信息录入失败")
            return 0
        
        # 登陆成功
        return 2
    
    # 检索，如果检索失败，则刷新之后，重新登陆，重新检索
    def retrievalTask(self):
        print(f"执行一次检索{self.keyWord}".center(50, "-"))
        time.sleep(1.5)
        while True:
            if not self.retrieval():
                self.pageRefresh()
                time.sleep(5)
                self.loginTask()
            else:
                break
        time.sleep(1.5)
    # 检索，并 将一页显示 50个
    def retrieval(self):
        time.sleep(1.5)
        # 输入智慧社区，点击检索按钮，点击一页显示 50个
        try:
            search_box = self.browser_window.find_element(By.CSS_SELECTOR, "#txt_1_value1")
            search_box.send_keys(self.keyWord)
            time.sleep(0.5)
            search_box.send_keys(Keys.SPACE)
            time.sleep(0.5)
            if random.random() > 0.5:
                self.browser_window.find_element(By.CSS_SELECTOR, ".search").click()
            else:
                search_box.send_keys(Keys.ENTER)
            time.sleep(2.5)
            # 点击选50个
            self.browser_window.find_elements(By.CSS_SELECTOR, "#perPageDiv .sort-list li")[2].click()
            time.sleep(2.5)
            # 获取总页数
            self.all_task_page = int(self.browser_window.find_element(By.CSS_SELECTOR, ".countPageMark").text.split('/')[-1])
        except Exception as e:
            print(f"检索失败, 错误信息：{e}")
            return False
        time.sleep(1.5)
        return True
    
    def ReaderListTask(self):
        print(f"获取列表：{self.keyWord}".center(50, "-"))
        # 如果session时间较长，则更新一下
        if time.perf_counter() - self.session_start_time > 15 * 60:
            self.loginTask()
            self.retrievalTask()
            self.toTargetPage()

        # 如果结果为0，那么就是出错了，等10s再抓一次
        # 如果还没有，就刷新页面，跳到应当到的页面
        read_list = self.HTMLReaderList()
        while True:
            if len(read_list) == 0:
                print("第一次获取列表失败, 准备10s后第二次获取")
                time.sleep(10)
                read_list = self.HTMLReaderList()
                if len(read_list) == 0:
                    print("第二次获取列表失败, 准备重新登录后，跳到指定页面获取")
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

    def HTMLReaderList(self):
        # self.currentPageTargetList = self.browser_window.find_elements(By.CSS_SELECTOR, '.operat a.icon-html')
        try:
            return self.browser_window.find_elements(By.CSS_SELECTOR, '.operat a.icon-html')
            time.sleep(1.5)
        except Exception as e:
            print(f"数据列表获取失败, 错误信息：{e}")
            return []
    
    # 刷新一下页面
    def pageRefresh(self):
        print(f"刷页面！".center(50, "-"))
        self.browser_window.refresh()
        time.sleep(2.5)
        pass

    pass

def main():
    cnki_newpaper = CNKI_NewsPaper_Loader("智慧社区", "D:/driver/107.0/chromedriver.exe", "user_name", "user_passerword")
    cnki_newpaper.startTask()
    cnki_newpaper.startGraspData()
    pass

if __name__ == '__main__':
    main()