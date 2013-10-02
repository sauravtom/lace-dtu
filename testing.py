
#import main

arr2 = [1234,5678,9101112]

def get_problems():
	p_arr=[]
	a_arr=[]
	text_file = open("problems.txt", "r")
	arr = text_file.read().split("!*QUES*!")
	return arr

def do(n):
	arr=get_problems()
	question = arr[n].split('!*ANS*!')[0]
	answer = arr[n].split('!*ANS*!')[1]
	answer = int(answer)
	print 'Question %s \n Answer %s' %(question,answer)
	print '%s == %s : %s' %(arr2[n],answer,answer == arr2[n])

if __name__ == "__main__":
	print "Enter index, starting from zero"
	n =int(raw_input())
	do(n)
