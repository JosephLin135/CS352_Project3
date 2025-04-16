echo no cookie base valid login cases - sucess
echo -e "\n------------------------------------------------------------------------------------"
echo curl -X POST -d "username=bezos&password=amazon" http://localhost:8000/
curl -X POST -d "username=bezos&password=amazon" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl -X POST -d "username=naiveuser&password=password123" http://localhost:8000/
curl -X POST -d "username=naiveuser&password=password123" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl -X POST -d "username=srinivas&password=nicetry" http://localhost:8000/
curl -X POST -d "username=srinivas&password=nicetry" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"

echo no cookie login tests with different inputs - bad cred 
echo curl -X POST -d "username=&password=" http://localhost:8000/
curl -X POST -d "username=&password=" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl -X POST -d "username=bezos&password=" http://localhost:8000/
curl -X POST -d "username=bezos&password=" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl -X POST -d "username=&password=amazon" http://localhost:8000/
curl -X POST -d "username=&password=amazon" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl -X POST -d "username=aaa&password=bbb" http://localhost:8000/
curl -X POST -d "username=aaa&password=bbb" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"

echo valid cookie testing
echo curl -c cookies.txt -X POST -d "username=bezos&password=amazon" http://localhost:8000/
curl -c cookies.txt -X POST -d "username=bezos&password=amazon" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"

echo curl -b cookies.txt -X POST -d "username=&password=" http://localhost:8000/
curl -b cookies.txt -X POST -d "username=&password=" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl -b cookies.txt -X POST -d "username=bezos&password=" http://localhost:8000/
curl -b cookies.txt -X POST -d "username=bezos&password=" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl -b cookies.txt -X POST -d "username=bezos&password=aaa" http://localhost:8000/
curl -b cookies.txt -X POST -d "username=bezos&password=aaa" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl -b cookies.txt -X POST -d "username=&password=amazon" http://localhost:8000/
curl -b cookies.txt -X POST -d "username=&password=amazon" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl -b cookies.txt -X POST -d "username=wow&password=amazon" http://localhost:8000/
curl -b cookies.txt -X POST -d "username=wow&password=amazon" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl -b cookies.txt -X POST -d "username=wow&password=yay" http://localhost:8000/
curl -b cookies.txt -X POST -d "username=wow&password=yay" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"

echo invalid cookie testing 
echo -e "\n------------------------------------------------------------------------------------"
echo curl --cookie "token=0" -X POST -d "username=&password=" http://localhost:8000/
curl --cookie "token=0" -X POST -d "username=&password=" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl --cookie "token=0" -X POST -d "username=bezos&password=" http://localhost:8000/
curl --cookie "token=0" -X POST -d "username=bezos&password=" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl --cookie "token=0" -X POST -d "username=&password=amazon" http://localhost:8000/
curl --cookie "token=0" -X POST -d "username=&password=amazon" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl --cookie "token=0" -X POST -d "username=bezos&password=bezos" http://localhost:8000/
curl --cookie "token=0" -X POST -d "username=bezos&password=amazon" http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"

echo logout testing 
echo curl -b cookies.txt -X POST -d action=logout http://localhost:8000/
curl -b cookies.txt -X POST -d action=logout http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"
echo curl --cookie "token=0" -X POST -d action=logout http://localhost:8000/
curl --cookie "token=0" -X POST -d action=logout http://localhost:8000/
echo -e "\n------------------------------------------------------------------------------------"