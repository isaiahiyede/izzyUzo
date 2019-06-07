
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from django.shortcuts import HttpResponse

import urllib
import cStringIO
from django.conf import settings
#import boto
from general.image_helpers import upload_image_To_s3, convert_remote_image_to_base64


class MyBarcodeDrawing(Drawing):
    def __init__(self, text_value, *args, **kw):
        barcode = createBarcodeDrawing('Code128', value=text_value,  barHeight=150, barWidth=2.0, humanReadable=True)
        Drawing.__init__(self,barcode.width,barcode.height,*args,**kw)
        self.add(barcode, name='barcode')







# def generate_package_barcode(package, package_id, location):
#     #if package.barcode_src is None:
#     #retrieve barcode_id
#     barcode_data = package.gen_barcode_id()
#
#     pkg_id = int(package_id)
#     #barcode_name = "package-%d" %pkg_id
#     barcode_name = "package-%s" %barcode_data
#     #print True
#     #save barcode source url
#     #package.barcode_src = "https://" + settings.AWS_STORAGE_BUCKET_NAME +".s3.amazonaws.com/barcodes/" + barcode_name + ".png"
#     #package.barcode_src = "%s%s/%s" %(settings.STATIC_URL, location, barcode_name+".png")
#
#     package.barcode_src = "%s%s/%s" %(settings.MEDIA_URL, 'export-barcodes', barcode_name+".png")
#     package.save()
#
#     #if hasattr(package, "order"):
#     #    barcode_data = "%s%s" %(pkg_id, "Z")
#     #else:
#     #    barcode_data = "%s%s" %("Z", pkg_id)
#
#
#
#     #barcode_data = pkg_id
#     #generated_barcode = MyBarcodeDrawing(pkg_id).save(formats=['png'], outDir=settings.FILES_ROOT, fnRoot=barcode_name)
#     generated_barcode = MyBarcodeDrawing(barcode_data).save(formats=['png'], outDir=settings.FILES_ROOT, fnRoot=barcode_name)
#     fp = urllib.urlopen(generated_barcode)
#     img = cStringIO.StringIO(fp.read())
#     #conn = boto.connect_s3()
#     conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
#     b = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
#     k = b.new_key('export-barcodes/%s' %generated_barcode[37:])
#     #k = b.new_key('%s/%s/%s' %(settings.MEDIA_LOCATION, location, generated_barcode[37:]))
#     k.set_contents_from_string(img.getvalue())
#
#     return "successful"


def generate_package_barcode(package, package_id, location):
    try:
        #import boto
        if package.barcode_src is None:
            #retrieve barcode_id
            #barcode_data = package.gen_barcode_id()
            barcode_data = package.tracking_number

            pkg_id = int(package_id)
            #barcode_name = "package-%d" %pkg_id
            #barcode_name = "package-%s" %barcode_data
            barcode_name = barcode_data
            #print 'barcode_name: ',barcode_name
            #print True
            #save barcode source url
            #package.barcode_src = "https://" + settings.AWS_STORAGE_BUCKET_NAME +".s3.amazonaws.com/barcodes/" + barcode_name + ".png"
            #package.barcode_src = "%s%s/%s" %(settings.STATIC_URL, location, barcode_name+".png")

            #barcode_data = pkg_id
            #generated_barcode = MyBarcodeDrawing(pkg_id).save(formats=['png'], outDir=settings.FILES_ROOT, fnRoot=barcode_name)
            generated_barcode = MyBarcodeDrawing(barcode_data).save(formats=['png'], outDir=settings.FILES_ROOT, fnRoot=barcode_name)
            fp = urllib.urlopen(generated_barcode)
            img = cStringIO.StringIO(fp.read())
            #conn = boto.connect_s3()
            # conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            # b = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
            # k = b.new_key('%s/%s' %(location, generated_barcode[37:]))
            # #k = b.new_key('%s/%s/%s' %(settings.MEDIA_LOCATION, location, generated_barcode[37:]))
            # k.set_contents_from_string(img.getvalue())

            filename = generated_barcode[37:]
            upload_image_To_s3(location, filename, img)

            barcode_src = "%s%s/%s" %(settings.STATIC_URL, location, barcode_name+".png")
            package.barcode_src = barcode_src
            package.barcode_base64 = convert_remote_image_to_base64(barcode_src)
            package.save()

            #if hasattr(package, "order"):
            #    barcode_data = "%s%s" %(pkg_id, "Z")
            #else:
            #    barcode_data = "%s%s" %("Z", pkg_id)




            return "successful"
        else:
            return "Already has barcode"
    except Exception as e:# ImportError, e:
        print 'generate barocde e: ',e
        return "Boto not available"


#user_passes_test(staff_check, login_url='/access-denied/')
def generate_barcode(request):
     approvedPackages = ShipmentPackage.objects.noBarcodeSrc()
     for package in approvedPackages:
          generate_package_barcode(package, package_id, "barcodes")

     return HttpResponse("it worked")


def create_test_barcode(request, barcode_id):#, tracking_number):
    #barcode_data = "%s%s" %(id, tracking_number)
    #barcode_data = "%s%s" %(id, "Z")
    # if shop_or_ship == "shipping":
    #     barcode_data = "%s%s" %("Z", id)
    # else:
    #     barcode_data = "%s%s" %(id, "Z")
    # print 'barcode_data :',barcode_data
    #generated_barcode = MyBarcodeDrawing(barcode_data).save(formats=['png'], outDir='C:\Users\ABIODUN\Dropbox\Work Related\TestBarcodes', fnRoot=id+ '.png')
    generated_barcode = MyBarcodeDrawing(barcode_id).save(formats=['png'], outDir='/Users/zaposta/Dropbox/Dropbox/Work-Related/TestBarcodes', fnRoot= barcode_id+ '.png')
    return HttpResponse (generated_barcode)
