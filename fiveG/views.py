from django.shortcuts import render
from .models import normalCol_read_mongo, collection_read_mongo, insert_document
import json
from django.core.paginator import Paginator
from django.http import HttpResponse
from .ml import calculateThroughput, displayDominateMap, detectUnnormalCell
import pandas as pd

# declare global variables
initialRecordNum = 108000
throughputCapacityData = collection_read_mongo(collection="main_file_with_UserTHR")

cursorLocation = 108000
oneTimeExtraRecord = 2280

def index(request):

    # use session to keep the offset value
    # num = request.session.get("num")
    # if not num:
    #     num = initialRecordNum
    # request.session["num"] = num

    # get main_file_with_UserThR collection from mongo

    result = calculateThroughput(throughputCapacityData[:initialRecordNum])
    dominateMap = displayDominateMap()

    context = {
        "UserThroughput": result,
        "map": dominateMap
    }

    return render(request, 'fiveG/index.html', context)


def show_normal_col_in_table(request):

    print("enter this function, enter this function, enter this function")
    if request.method == "GET":



        print(request.GET)
        limit = request.GET.get('limit')  # how many items per page
        offset = request.GET.get('offset')  # how many items in total in the DB
        search = request.GET.get('search')
        sort_column = request.GET.get('sort')  # which column need to sort
        order = request.GET.get('order')  # ascending or descending
        if search:
            # all_records = collection_read_mongo(collection="event_log")
            all_records = pd.DataFrame.from_dict(detectUnnormalCell())
        else:
            # all_records = collection_read_mongo(collection="event_log")
            all_records = pd.DataFrame.from_dict(detectUnnormalCell())

        # all_records = all_records.insert(0, "order", range(0, len(all_records.index)))

        # all_records_count = len(all_records.index)
        all_records_count = 100
        if not offset:
            offset = 0
        if not limit:
            limit = 10

        all_records_list = all_records[:100].values.tolist()
        pageinator = Paginator(all_records_list, limit)

        page = int(int(offset) / int(limit) + 1)
        response_data = {'total': all_records_count, 'rows': []}

        for record in pageinator.page(page):
            print(record)

            response_data['rows'].append({
                # "time": record[0] if record[0] else "",
                # "X": record[1] if record[1] else "",
                # "Y": record[2] if record[2] else "",
                # "IMSI": record[3] if record[3] else "",
                # "EVENT": record[4] if record[4] else "",
                # "RSRQ": record[5] if record[5] else "",
                # "CellID": record[6] if record[6] else ""
                "CellID": record[0] if record[0] else "",
                "userID": record[2] if record[2] else "",
                "signal": record[1] if record[1] else ""
            })

        return HttpResponse(json.dumps(response_data))


def displayDemo(request):


    template_names = "fiveG/displayDemo.html"

    normalCol = normalCol_read_mongo()


    context = {}
    # print(template_names[:1])

    return render(request, template_names)


def loadMore(request):
    global cursorLocation
    global oneTimeExtraRecord
    if request.method == "GET":
        nextCursorLocation = cursorLocation + oneTimeExtraRecord
        thisResult = calculateThroughput(throughputCapacityData[cursorLocation:nextCursorLocation])
        cursorLocation = nextCursorLocation
        return HttpResponse(json.dumps(thisResult))
    else:
        return 0

def controlPanel(request):
    if request.method == "GET":
        if request.GET.get("cellID") == "":
            cellID = 0
        else:
            cellID = request.GET.get("cellID")

        if request.GET.get("normal") != None:
            normal = request.GET.get("normal")
        else:
            normal = 0

        if request.GET.get("outage") != None:
            outage = request.GET.get("outage")
        else:
            outage = 0

        if request.GET.get("coc") != None:
            coc = request.GET.get("coc")
        else:
            coc = 0

        if request.GET.get("cco") != None:
            cco = request.GET.get("cco")
        else:
            cco = 0

        if request.GET.get("mro") != None:
            mro = request.GET.get("mro")
        else:
            mro = 0

        if request.GET.get("mlb") != None:
            mlb = request.GET.get("mlb")
        else:
            mlb = 0

        document = {"cellID": cellID,
                    "normal": normal,
                    "outage": outage,
                    "coc": coc,
                    "cco": cco,
                    "mro": mro,
                    "mlb": mlb
                    }

        if cellID == 0:
            info = "Warning, the control Panel encounters problems, fixing"
            return HttpResponse(json.dumps(info))
        else:
            # store this operation into mongoDB collecton - control Panel
            # insert one document into database
            info = "successfully finish new operation"
            insert_document("controlpanel", document)
            return HttpResponse(json.dumps(info))





