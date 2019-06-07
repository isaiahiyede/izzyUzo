from sokohaliAdmin.models import ShippingKeyword, CostCalcSettings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from general.custom_functions import country_freight_costs


def costcalc_settings():
    cost_settings = CostCalcSettings.objects.get(pk = 1)
    return cost_settings


#divide shipping keywords string
class ListBisectionSearch():
    def __init__(self, listToSearch):
        self.listToSearch = listToSearch

    def listLen(self):
        return len(self.listToSearch)

    def divideList(self):
        #check if keyword list has one or more words
        listLen = self.listLen()
        if listLen > 2:
            half = listLen/2
            return self.listToSearch[:half], self.listToSearch[half:]
        return self.listToSearch, self.listToSearch

    def keywordProbableList(self, keyword):
        #check if keyword list has one or more words
        if self.listLen() > 10: #minimum number of keywords
            firstList, secondList = self.divideList()
            lastWord = firstList[-1]
            try:
                if keyword[0] > lastWord[0]:
                    return secondList
            except:
                return firstList
        return self.listToSearch

    def findKeyword(self, keyword):
        #convert keyword to lowercase
        keyword = keyword.lower()
        #to deal with prefixes
        #print "keyword 1: ",keyword
        if len(keyword) >= 3:
            #print "keyword: ",keyword
            probableList = self.keywordProbableList(keyword)

            #print "probableList %s" %probableList
            ##print probableList
            #matching = filter(lambda x: keyword in x, probableList)
            ##print "keyword: %s" %keyword
            matching = filter(lambda x: keyword == x, probableList)
            ##print "matching :%s" %matching
            if len(matching) > 0:
                #print "keyword 2 %s" %keyword
                return True
        return False

#add/or not s to category description
def singPlurKwdCategory(qty, category):
    if qty > 1 and category[-1] != 's':
        return category +'s'
    elif qty == 1 and category[-1] == 's':
        beforeLast = len(category)-1
        return category[0 : beforeLast]
    return category

#construct matching keyword text
def matchingKeywordInfo(keyWeight_dict, keyQty_dict):
    if len(keyWeight_dict) > 0:
        weights = keyWeight_dict.values()
        max_weight = max(weights)

        keywordCategory = ""
        for key, val in keyWeight_dict.items():
            if max_weight == val:
                keywordCategory = key
        #category = singPlurKwdCategory(keyQty_dict[keywordCategory], keywordCategory)
        #return "%d %s" %(keyQty_dict[keywordCategory], category)
        return "%d %s" %(keyQty_dict[keywordCategory], keywordCategory)
    return ""


#convert item description into a list of keywords
def desription_keywords(description):
    ##print "description: %s" %description
    self_desc = description.lower()
    #mod_desc = self_desc.replace("(", "").replace(")","").replace(",", "").replace("and", "").replace("the", "").replace("with", "")
    mod_desc = self_desc.replace("(", "").replace(")","").replace(",", "")#.replace("-", " ")
    modDescList = mod_desc.split(" ")
    modDescList.sort()
    newKeywordsLt = filter(None, modDescList)
    newKeywordsList = [x for x in newKeywordsLt ]#if x.isalpha() or "-" in x]
    ##print "newKeywordsList %s" %newKeywordsList
    #newKeywordsList = [x for x in newKeywordsLt if x.isalpha() or "-" in x]
    ##print "newKeywordsList %s" %newKeywordsList
    return newKeywordsList


#extract description, quantity, listed_price_D and country
def description_and_quantity(product):
    try:
          description = product.description
          quantity = int(product.quantity)
          country = product.country
          try:
               listed_price_D = float(getattr(product, "listed_price_D"))#product.listed_price_D
          except:
               listed_price_D = float(getattr(product, "total_value"))
    except:
          description = product["description"]
          quantity = int(product["quantity"])
          listed_price_D = float(product["price"])
          country = product["country"].lower()

    return description, quantity, listed_price_D, country

# % of price for no matching keyword
def weightForNoMatchingKywd(costcalc, no_match_value, country, marketing_member, origin, destination):
    delivery_method_rates = marketing_member.get_route_delivery_method_rates(origin, destination, 'air')#, 3.4)
    print delivery_method_rates
    weight_charge_list = []
    for obj in delivery_method_rates:
        weight_charge_list.append((obj.rate_D, obj.rate_D * float(obj.to_range)))

    print 'weight_charge_list: ', weight_charge_list

    #costcalc = costcalc_settings()
    noMatchValWeightDet = (float(costcalc.kwd_val_percentage)/100) * no_match_value
    #weight in lbs and corresponding charge
    #unitAirFreightCost, unitAirFreight1Cost, unitAirFreight2Cost, unitAirFreight3Cost, \
    #unitAirFreight4Cost, unitAirFreight5Cost, exchange_rate = country_freight_costs(costcalc, country)

    #weight_charge_list = [(unitAirFreight1Cost, unitAirFreight1Cost * 4), (unitAirFreight2Cost, unitAirFreight2Cost * 10), (unitAirFreight3Cost, unitAirFreight3Cost*20), (unitAirFreight4Cost, unitAirFreight4Cost*50), (unitAirFreight5Cost, unitAirFreight5Cost*250)]

    #weight_charge_list = [(costcalc.unit_cost_air_freight_1, costcalc.unit_cost_air_freight_1 * 4), (costcalc.unit_cost_air_freight_2, costcalc.unit_cost_air_freight_2 * 10), (costcalc.unit_cost_air_freight_3,costcalc.unit_cost_air_freight_3*20), (costcalc.unit_cost_air_freight_4,costcalc.unit_cost_air_freight_4*50), (costcalc.unit_cost_air_freight_5, costcalc.unit_cost_air_freight_5*250)]

    for weight, charge in weight_charge_list:
        if noMatchValWeightDet < charge:
            print weight, charge
            print "noMatchValWeightDet: %s" %noMatchValWeightDet
            no_match_weight = round(float(noMatchValWeightDet) / weight, 2)
            if no_match_weight < 1:
                return 1 #minimum weight is 1 lbs
            print "no_match_weight: %s" %no_match_weight
            return no_match_weight

    weight_charge_upper = weight_charge_list[-1]
    sug_weight = (noMatchValWeightDet * weight_charge_upper[0]) / (weight_charge_upper[1])
    return sug_weight

#find item description keyword from shipping keyword object
def find_keyword(sorted_keywords_list, keyword):
    lBS = ListBisectionSearch(sorted_keywords_list)
    ##print "lBS %s" %lBS
    #print "lBS.findKeyword(keyword): ",lBS.findKeyword(keyword)
    return lBS.findKeyword(keyword)
    #lBS = ListBisectionSearch()
    #return lBS.findKeyword(keyword, sorted_keywords_list)

#shipping keyword objects with matching keyword
def shippingKeywordListForKeyword(keyword, shippingKeywordList, detector_or_mgr):
    shippingKeywordObjs = []
    #shippingKeywordList = ShippingKeyword.objects.filter(~Q(category = "Unmatched list 1"), ~Q(category = "Unmatched list 2"))#all()#_keywords()
    for sKList in shippingKeywordList:
        ##print "sKList.sorted_keywords_list(None): ",sKList.sorted_keywords_list(None)
        #print "sKList.sorted_keywords_list(detector_or_mgr): ",sKList.sorted_keywords_list(detector_or_mgr)
        match = find_keyword(sKList.sorted_keywords_list(detector_or_mgr), keyword)
        #print "match: ",match
        ##print "keyword-1 %s" %keyword
        if match:
            shippingKeywordObjs.append(sKList)
    return shippingKeywordObjs



def matchingShippingKeywordObjs(desc_keywords, product_quantity):
    sKObjs = []
    matchingKeywords = []
    keyWeight_dict = {}
    keyQty_dict = {}
    shippingKeywordList = ShippingKeyword.objects.filter(~Q(category = "Unmatched list"))#, ~Q(category = "Unmatched list 2"))#all()#_keywords()

    # # unmatched_keywords_list_1 = get_object_or_404(ShippingKeyword, category = "Unmatched list 1")
    # # unmatched_keywords_list_2 = get_object_or_404(ShippingKeyword, category = "Unmatched list 2")
    # #
    # # un_matched_keywords_list = unmatched_keywords_list_2.sorted_keywords_list()
    #List of un-matched keywords
    unmatched_keywords = ""
    #print "desc_keywords %s" %desc_keywords
    for keyword in desc_keywords:
        ##print keyword
        no_match = False
        for sKList in shippingKeywordList:

            match = find_keyword(sKList.sorted_keywords_list(), keyword)
            ##print "keyword-1 %s" %keyword
            if match:
                ##print "checking for keyword that exists: %s" %keyword
                ##print "found keyword %s" %keyword
                sKObjs.append(sKList)
                matching_keyword = "%d %s" %(product_quantity, keyword)
                matchingKeywords.append(str(matching_keyword))

                #keyWeight_dict[sKList.category] = sKList.shipping_box.box_weight
                keyWeight_dict[sKList.category] = sKList.shipping_box.min_weight()

                keyQty_dict[sKList.category] = product_quantity

                no_match = True
            #else:

    # #     #if no matching keyword, save keyword in db
    # #     if not no_match:
    # #         if not find_keyword(un_matched_keywords_list, keyword):
    # #
    # #             #check if keyword is a string
    # #             # if keyword.isalpha() == True or "-" in keyword:
    # #             #     #print "checking for keyword that does not exist"
    # #             #     try:
    # #             #         keyword.decode()
    # #             #         unmatched_keywords += ", %s" %keyword#.lower()
    # #             #     except:
    # #             #         pass
    # #
    # #             try:
    # #                 ##print "checking for keyword that does not exist: %s" %keyword
    # #                 keyword.decode()
    # #                 unmatched_keywords += ", %s" %keyword#.lower()
    # #             except:
    # #                 pass
    # #
    # # #update un-matched keywords in database
    # # unmatched_keywords_list_1.keywords += unmatched_keywords
    # # unmatched_keywords_list_1.save()
    # #
    # # unmatched_keywords_list_2.keywords += unmatched_keywords
    # # unmatched_keywords_list_2.save()


    matchingKwdInfo = matchingKeywordInfo(keyWeight_dict, keyQty_dict)
    return sKObjs, matchingKwdInfo#matchingKeywords


def maxWeightMatchingShpKywds(desc_keywords, product_quantity):
    sKObjWeights = []
    sKObjs, matchingKeywords = matchingShippingKeywordObjs(desc_keywords, product_quantity)

    ##print 'desc_keywords: %s ,product_quantity: %s' %(desc_keywords, product_quantity)

    for obj in sKObjs:
        #sKObjWeights.append(float(obj.shipping_box.box_weight) * product_quantity)
        sKObjWeights.append(float(obj.shipping_box.min_weight()) * product_quantity)

    if len(sKObjWeights) > 0:
        return matchingKeywords, max(sKObjWeights)
    return matchingKeywords, 0


def unpack_kwd_dict(kwd_dict):
    matchingKeywords_info = ""
    for key, val in kwd_dict.iteritems():
        matchingKeywords_info += "%d %s, " %(val, singPlurKwdCategory(val, key))
    return matchingKeywords_info

def split_qty_kwds(keyword_match):
    ##print "keyword_match %s" %keyword_match
    splitted_kwd_match = keyword_match.split(" ")
    qty = int(splitted_kwd_match[0])
    kwd_match = splitted_kwd_match[1: len(splitted_kwd_match)]
    return qty, ' '.join(kwd_match)

def suggestedWeightAndInfo(products, costcalc, marketing_member, origin, destination):
    no_match_count = 0
    no_match_value = 0
    suggestedWeights = []
    matchingKeywords_info = ""
    matching_keywords_dict = {}
    count = 1
    products_count = len(products)#products.count()
    loop_count = 0

    unmatched_keywords = ""
    unmatched_keywords_list_1 = get_object_or_404(ShippingKeyword, category = "Unmatched list")
    #unmatched_keywords_list_2 = get_object_or_404(ShippingKeyword, category = "Unmatched list 2")
    print "unmatched_keywords_list_1:", unmatched_keywords_list_1
    un_matched_keywords_list = unmatched_keywords_list_1.sorted_keywords_list()
    ##print "un_matched_keywords_list %s" %un_matched_keywords_list

    for product in products:
        loop_count += 1

        #country = product.country

        description, quantity, listed_price_D, country = description_and_quantity(product)

        desc_keywords = desription_keywords(description)
        print 'desc_keywords-1 %s' %desc_keywords
        test_weight = None

        try:
            #weight = float(getattr(product, "unit_weight"))
            test_weight = float(product["unit_weight"]) * quantity
            print 'test_weight inside the try :', test_weight, '\n'

            if test_weight <= 0:
                test_weight = None
                print 'test_weight inside the if :', test_weight, '\n'

            else:
                print 'test_weight inside the else :', test_weight, '\n'
                suggestedWeights.append(test_weight)

        except:
            print 'test_weight inside the except :', test_weight, '\n'
            pass

        if test_weight is None:
            print 'test_weight inside the if None  :', test_weight, '\n'

            matchingKeywords, weight = maxWeightMatchingShpKywds(desc_keywords, quantity)
            print 'matchingKeywords: %s, suggested weight: %s' %(matchingKeywords, weight)

            if len(matchingKeywords) > 0 and weight != "":
                stripped_matching_kwds = str(matchingKeywords).strip('[]').strip("''")
                qty, kwd_match_text = split_qty_kwds(stripped_matching_kwds)

                print "matchingKeywords_info: %s" %stripped_matching_kwds
                print "matching_keywords_dict %s" %matching_keywords_dict
                if matching_keywords_dict.has_key(kwd_match_text):
                    qty = matching_keywords_dict[kwd_match_text]
                    matching_keywords_dict[kwd_match_text] = qty + quantity
                else:
                    matching_keywords_dict[kwd_match_text] = qty

                matchingKeywords_info += stripped_matching_kwds

                #if loop_count < products_count:
                #    matchingKeywords_info += ", "
                suggestedWeights.append(weight)
                print "matchingKeywords_info: %s" %matchingKeywords_info

            else:
                no_match_count += quantity
                no_match_value += (quantity * listed_price_D)
                print 'no_match_value: ', no_match_value, '\n'

                print "find_keyword(un_matched_keywords_list, description): %s" %find_keyword(un_matched_keywords_list, description)
                if not find_keyword(un_matched_keywords_list, description):
                    #confirm that product description is a string
                    try:
                        description.decode()
                        unmatched_keywords += ", %s" %description.lower()
                        print 'product description: %s' %description
                    except:
                        pass


                suggestedWeights.append(weightForNoMatchingKywd(costcalc, no_match_value, country, marketing_member, origin, destination))



    #update un-matched keywords in database
    unmatched_keywords_list_1.keywords += unmatched_keywords
    unmatched_keywords_list_1.save()

        ##print "matchingKeywords_info %s" %matchingKeywords_info
        ##print 'suggestedWeights : ', suggestedWeights, '\n'

    #check if matchingKeywords_info is not empty
    #if len(matchingKeywords_info) > 1:
    #    #print "matchingKeywords_info: %s" %matchingKeywords_info
    #
    #    firsthalf = matchingKeywords_info.split(",")
    #    #print "firsthalf %s" %firsthalf
    ##print "matchingKeywords_info: %s" %matchingKeywords_info
    ##print "matching_keywords_dict %s" %unpack_kwd_dict(matching_keywords_dict)

    matchingKeywords_info = unpack_kwd_dict(matching_keywords_dict)
    suggestedWeight = sum(suggestedWeights)

    if no_match_count > 0:
        if len(matchingKeywords_info) == 0:
            matchingKeywords_info += "Your %d %s" %(no_match_count, singPlurKwdCategory(no_match_count, "items"))
        else:
            matchingKeywords_info += "and your %d other %s" %(no_match_count, singPlurKwdCategory(no_match_count, "items"))
    else:
        matchingKeywords_info = matchingKeywords_info[:-2]
    ##print "matchingKeywords_info: %s" %matchingKeywords_info
    ##print "matchingKeywords_info[:-1]: %s" %matchingKeywords_info[:-2]
    return suggestedWeight ,matchingKeywords_info
