from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import LeaveSerializer
from .serializer import CustomUserSerializer
from django.conf import settings
from django.contrib.auth import authenticate
from .models import Leave, CustomUser
from django.core.mail import send_mail
import urllib.request
import json
import requests
import json
import urllib.request
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.decorators import api_view

class AccountView(APIView):

    @staticmethod
    @api_view(['POST'])
    def addaccount(request):
        userFirstname = request.data.get('firstname')
        userLastname = request.data.get('lastname')
        userMail = request.data.get('email')
        userPassword = request.data.get('password')
        is_admin = request.data.get('is_admin')
        userGender = request.data.get('gender')

        if(userGender == "Male"):
            serializer_data = {
                    "username":userFirstname + userLastname,
                    "userfirstname":userFirstname,
                    "userlastname":userLastname,
                    "email":userMail,
                    "password":userPassword,
                    "is_admin":is_admin,
                    "gender":userGender,
                    "paternity":3,
                    "maternity":0,
                    "paid":30,
                    "rtt":0,
                    #"leaveid":leave
            }
        if(userGender == "Female"):
            serializer_data = {
                    "username":userFirstname + userLastname,
                    "userfirstname":userFirstname,
                    "userlastname":userLastname,
                    "email":userMail,
                    "password":userPassword,
                    "is_admin":is_admin,
                    "gender":userGender,
                    "paternity":0,
                    "maternity":60,
                    "paid":30,
                    "rtt":0,
            }

        serializer = CustomUserSerializer(data=serializer_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            print(serializer.errors)
            return Response({
                'status': 'error',
                'agrs':serializer.errors,
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def get(self,request):
        users = CustomUser.objects.filter()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    @staticmethod
    @api_view(['POST'])
    def addleave(request):
        startDate = request.data.get("startdate")
        endtDate = request.data.get("enddate")
        leaveType = request.data.get("leavetype")
        leaveDays = request.data.get("days")
        userID = request.data.get("userid")

        serializer_data = {}
        try:
            user = CustomUser.objects.get(id=userID)
            # only accept these 4 strings as a leave type
            if leaveType not in ("paid","paternity","maternity","rtt"):
                return Response({'status':'error','args': 'leave type must either be: paid,paternity,maternity or rtt',},status=status.HTTP_400_BAD_REQUEST)
            if(leaveDays == 0):
                return Response({'status':'error','args': 'leave days must be > 0',},status=status.HTTP_400_BAD_REQUEST)
            if(leaveType == "paid" and user.paid < int(leaveDays)):
               return Response({'status':'error','args': 'The days you selected are more than your available paid days',},status=status.HTTP_400_BAD_REQUEST)
            if(leaveType == "paternity" and user.paternity < int(leaveDays)):
                return Response({'status':'error','args': 'The days you selected are  more than your available paternity days',},status=status.HTTP_400_BAD_REQUEST)
            if(leaveType == "maternity" and user.maternity < int(leaveDays)):
                return Response({'status':'error','args': 'The days you selected are  more than your available maternity days',},status=status.HTTP_400_BAD_REQUEST)
            if(leaveType == "rtt" and user.rtt < int(leaveDays)):
                return Response({'status':'error','args': 'The days you selected are  more than your available rtt days',},status=status.HTTP_400_BAD_REQUEST)
           
        except:
             return Response({
                 'status':'error',
                 'args': 'no user with this id exist',
            },status=status.HTTP_204_NO_CONTENT)
        
        serializer_data = {
                "startdate":startDate,
                "enddate":endtDate,
                "leavetype":leaveType,
                "days":leaveDays,
                "userid":userID,
                "status":"pending",
        }
 
        print(serializer_data)
        serializer = LeaveSerializer(data=serializer_data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status':'success',
                'args': 'leave apply successfully sent',
            })
            return Response(serializer.data)
        else:
            return Response({
                'status': 'error',
                'agrs':serializer.errors,
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    @api_view(['GET'])
    def getuserleaves(request):
        userID = request.GET.get('id')
        leaves = Leave.objects.filter(userid=userID)
        serializer = LeaveSerializer(leaves, many=True)
        
        return Response(serializer.data)

    @staticmethod
    @api_view(['GET'])
    def getuser(request):
        userID = request.GET.get('id')
        user = CustomUser.objects.filter(id=userID)
        serializer = CustomUserSerializer(user, many=True)
        return Response(serializer.data)

    @staticmethod
    @api_view(['GET'])
    def getallleaves(request):
        leaves = Leave.objects.filter()
        serializer = LeaveSerializer(leaves, many=True)
        return Response(serializer.data)

    @staticmethod
    @api_view(['DELETE'])
    def deleteleave(request):
        leaveID = request.GET.get("id")
        try:
           Leave.objects.filter(id=leaveID).delete()
            
        except:
             return Response({
                'status': 'error',
                'args':'no leave with this id exist',
            },status=status.HTTP_204_NO_CONTENT)
        
        leaves = Leave.objects.filter()
        serializer = LeaveSerializer(leaves, many=True)
        return Response({
                'status': 'success',
                'args':serializer.data,
            })
        
    @staticmethod
    @api_view(['PATCH'])
    def updateleave(request):
        
        leavestatus = request.data.get("status")
        leaveID = request.data.get("leaveid")
        leave = Leave.objects.filter(id=leaveID).first()
        data = {
            "status": leavestatus,
            }
        type = ""
        if leavestatus not in ("approved","canceled"):
             return Response({'status': 'error',
                             'args':'leave status must be changed to either approved or canceled'},status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LeaveSerializer(leave,data=data,partial=True)# updating leave status
        if serializer.is_valid():
               serializer.save() # updating leave status
               user = CustomUser.objects.filter(id=leave.userid).first()
               data = {}
               if leave.leavetype == "paid":
                   type = "payé"
               if leave.leavetype == "paternity":
                   type = "paternité"
               if leave.leavetype == "maternity":
                    type = "maternité"
               if leave.leavetype == "rtt":
                    type = "RTT"
               if leavestatus == "approved":
                  if leave.leavetype == "paid":
                      data = {
                        "paid": user.paid - leave.days,
                        }
                  if leave.leavetype == "paternity":
                      data = {
                        "paternity": user.paternity - leave.days,
                        }
                  if leave.leavetype == "maternity":
                       data = {
                         "maternity": user.maternity - leave.days,
                         }
                  if leave.leavetype == "rtt":
                       data = {
                         "rtt": user.rtt - leave.days,
                         }
               serializer = CustomUserSerializer(user,data=data,partial=True)# updating user status
               if serializer.is_valid():
                   serializer.save() # updating user status
                   leaves = Leave.objects.filter()
                   serializer = LeaveSerializer(leaves, many=True)
               return Response({
                     'status': 'success',
                     'agrs':serializer.data,
                 })
            
        else:
             return Response({
                'status': 'error',
                'agrs':serializer.errors,
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @staticmethod
    @api_view(['POST'])
    def login(request):
        userPass = request.data.get("password")
        userMail = request.data.get("email")
        try:
            # Try to find a user matching userMail
            user = CustomUser.objects.get(email=userMail)

            #  Check the password if it match
            if (userPass == user.password):
                # Yes?  return a user
                #leaveInfo = Leave.objects.filter(id = user.leaveid)
                #serializer = LeaveSerializer(leaveInfo, many = True)
                serializer = CustomUserSerializer(user)
                response = {'status':'success',
                            'args':serializer.data},
                code=status.HTTP_200_OK
            else:
                # No?  login failed, return false
                response = {'status': 'error',
                            'args':'wrong password'},
                code=status.HTTP_401_UNAUTHORIZED
        except:
            # No user was found, return false
            response = {'status': 'error',
                        'args':'no user with this email found'},
            code=status.HTTP_204_NO_CONTENT
        return Response(response,status=code)
