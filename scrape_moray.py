import requests
from bs4 import BeautifulSoup 
import json


def scrape(url):
	home = 'http://www.moray.gov.uk'
	html = requests.get(url).text
	soup = BeautifulSoup(html, features="html.parser")
	all_ulists = soup.find_all("ul")
	request_list = []
	month_links = []
	for ulist in all_ulists:
		link_list = ulist.find_all("a")
		for link in link_list:
			if link["href"] != "#":
				month_links.append(link["href"])
	# month_links = ["/moray_standard/page_140447.html"]		# For testing smaller sample set
	for month in month_links:
		month_url = home + month
		raw_month = requests.get(month_url).text
		month_soup = BeautifulSoup(raw_month, features="html.parser")
		table = month_soup.table
		rows = table.find_all("tr")
		rows.pop(0)		# Removes table header
		date_tracker = ""
		for row in rows:
			row_data = row.find_all("td")
			temp_date = row_data[0].contents[0]
			if temp_date != " ":		# Carries date down table until new date
				date_tracker = temp_date
			date = date_tracker
			if len(row_data) > 2:  # IJB table has no department column
				department = row_data[2].contents[0]
			else:
				department = "Integrated Joint Board"
			name, number, request_url = process_link(row_data, home)

			request_list.append(FOIRequest(date, name, department, request_url, number))

	return request_list


def process_link(row_data, home):
	link_data = row_data[1].a
	if link_data:  # At least once instance of no link provided
		rel_url = link_data["href"]
		name = link_data.contents[0]
		request_url = home + rel_url

		raw_request = requests.get(request_url).text
		request_soup = BeautifulSoup(raw_request, features="html.parser")
		try:  # At least one instance of <strong> inside h2
			number = request_soup.h2.contents[0][8:]
		except:
			number = "#"
	else:
		name = row_data[1].contents[0]
		number = "#"
		request_url = "#"

	return name, number, request_url


class FOIRequest:
	def __init__(self, date, name, department, request_url, request_number):
		self.date = date
		self.name = name
		self.department = department
		self.url = request_url
		self.number = request_number

	def __repr__(self):
		return f"[Dpt:{self.department}] {self.name}({self.number})[{self.date}]: {self.url}"


url = 'http://www.moray.gov.uk/moray_standard/page_62338.html'
request_index = scrape(url)

request_json = json.dumps([obj.__dict__ for obj in request_index])

with open('json_outputs/moray_foi_json.txt', 'w') as file:
	file.write(request_json)
