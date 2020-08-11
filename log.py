import os
import ast
from datetime import datetime
from dateutil import tz
import pprint


class HistLog:
    __DATETIME_FORMAT      = "%a, %b %d %Y %I:%M%p"

    __LOCAL_TIMEZONE       = tz.tzlocal()
    __PST_TIMEZONE         = tz.gettz("US/Alaska") # Alaska timezone, guards against Pacific Daylight Savings Time

    __MAX_HIST_LEN         = 5 # days


    def __init__(self, q_elements_path, q_state_path, curr_q_datetime=datetime.now()):
        self.q_elements_path = q_elements_path
        self.q_state_path = q_state_path

        self.__curr_q_datetime = curr_q_datetime.replace(tzinfo=self.__LOCAL_TIMEZONE)
        self.q_elements = self.__read_dict(q_elements_path)
        # q_state = {'current' : q_num, 'url' : {q_num: url}}
        self.q_state = self.__read_dict(q_state_path)
        if self.q_state is None:
            self.q_state = {'current':176,'url':{}}

    def __read_dict(self, path):
        if os.path.exists(path):
            try:
                file = open(path, "r")
                return ast.literal_eval(file.read())
            except:
                pass
        return None

    def write_dict(self, dict, path):
        file=open(path, 'w')
        pprint.pprint(dict, file)

    def update_q_current(self, q_num):
        self.q_state['current'] = q_num

    def update_q_url(self, q_num, url):
        self.q_state['url'][q_num] = url

    def update_q_state(self, q_num, url):
        self.update_q_current(q_num)
        self.update_q_url(q_num, url)
        self.write_dict(self.q_state, self.q_state_path)









    #----------    potentially deprec ------------------------
    def __read_deprec(self, path):
        if not os.path.exists(path):
            return []
        else:
            with open(path, "r") as log:
                return [line.strip("\n") for line in log.readlines()]

    def get_timestamp(self):
        return self.__run_datetime.strftime(self.__DATETIME_FORMAT)


    def deprec_get_completion(self):
        # check if already ran today
        if len(self.__run_hist) > 0:
            print(self.__run_hist[-1].split(": "))
            last_ran, completed = self.__run_hist[-1].split(": ")

            last_ran_pst = datetime.strptime(last_ran, self.__DATETIME_FORMAT).replace(tzinfo=self.__LOCAL_TIMEZONE).astimezone(self.__PST_TIMEZONE)
            run_datetime_pst = self.__run_datetime.astimezone(self.__PST_TIMEZONE)
            delta_days = (run_datetime_pst.date()-last_ran_pst.date()).days
            is_already_ran_today = ((delta_days == 0 and last_ran_pst.hour >= self.__RESET_HOUR) or (delta_days == 1 and run_datetime_pst.hour < self.__RESET_HOUR))
            if is_already_ran_today:
                if completed == self.__COMPLETED_TRUE:
                    self.__completion.edge_search = True
                    self.__completion.web_search = True
                    self.__completion.mobile_search = True
                    self.__completion.offers = True
                else:
                    if self.__EDGE_SEARCH_OPTION not in completed:
                        self.__completion.edge_search = True
                    if self.__WEB_SEARCH_OPTION not in completed:
                        self.__completion.web_search = True
                    if self.__MOBILE_SEARCH_OPTION not in completed:
                        self.__completion.mobile_search = True
                    if self.__OFFERS_OPTION not in completed:
                        self.__completion.offers = True
            else:
                self.__search_hist = []

        if not self.__completion.is_all_completed():
            # update hist with todays time stamp
            self.__run_hist.append(self.get_timestamp())
            if len(self.__run_hist) == self.__MAX_HIST_LEN:
                self.__run_hist = self.__run_hist[1:]

        return self.__completion
    def get_search_hist(self):
        return self.__search_hist


    def deprec_write(self, completion, search_hist):
        self.__completion.update(completion)
        if not self.__completion.is_all_completed():
            failed = []
            if not self.__completion.is_edge_search_completed():
                failed.append(self.__EDGE_SEARCH_OPTION)
            if not self.__completion.is_web_search_completed():
                failed.append(self.__WEB_SEARCH_OPTION)
            if not self.__completion.is_mobile_search_completed():
                failed.append(self.__MOBILE_SEARCH_OPTION)
            if not self.__completion.is_offers_completed():
                failed.append(self.__OFFERS_OPTION)
            failed = ', '.join(failed)
            msg = self.__COMPLETED_FALSE.format(failed) 
        else:
            msg = self.__COMPLETED_TRUE

        if self.__COMPLETED_TRUE not in self.__run_hist[-1]:
            self.__run_hist[-1] = "{}: {}".format(self.__run_hist[-1], msg)

        with open(self.run_path, "w") as log:
            log.write("\n".join(self.__run_hist) + "\n")

        if search_hist:
            for query in search_hist:
                if query not in self.__search_hist:
                    self.__search_hist.append(query)
            #to avoid UnicodeEncodeErrors
            self.__search_hist = [hist.encode('ascii', 'ignore').decode('ascii') for hist in self.__search_hist]
            with open(self.search_path, "w") as log:
                log.write("\n".join(self.__search_hist) + "\n")


