from cities_light import models as world_geo_data


def pkg_origin_destination_distributor(request, pkg):
    marketer            = pkg.user.useraccount.marketer
    marketer_code       = marketer.random_code
    org_dest            = pkg.tracking_number.split(marketer_code)
    split_org_dest      = org_dest[1].split('-')
    origin_code         = split_org_dest[0]
    destination_code    = split_org_dest[1]

    origin              = world_geo_data.Country.objects.get(code3 = origin_code)
    destination         = world_geo_data.Country.objects.get(code3 = destination_code)

    shipping_chain      = marketer.get_shipping_chain_route(origin, destination)

    return shipping_chain.origin_distributor, shipping_chain.destination_distributor


def origin_distributor_access(request, pkg):
    origin_distributor, destination_distributor = pkg_origin_destination_distributor(request, pkg)

    return origin_distributor, origin_distributor.has_api
