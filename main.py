#!/usr/bin/env python

import controller as Controller

def main():
	controller = Controller.Controller(name = 'Player 1')
	controller.open_device()
	
	controller.list_keys()
		
	controller.click_key('A')
	controller.click_key('X')
	controller.click_key('h')	
	
	controller.close_device()

if __name__ == "__main__":
	main()
