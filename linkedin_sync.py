import json

from bunch import Bunch

from models.linkedin_profile import LinkedInProfile

fp = "/Users/candacechatman/dev/lchop/data/profile.json"

from jinja2 import Template




with open(fp, "r") as f:
    data = Bunch(json.loads(f.read()))

    profiles = LinkedInProfile.get_all()

    # Create a first and last name dict
    people = {}
    for profile in data.elements:
        people[profile['firstName'] + profile['lastName']] = profile

    # find the profile in the elements by checking against first and last name
    for profile in profiles:
        person = people.get(profile.firstName + profile.lastName)
        #                 <img src="{{ profile.profilePictureDisplayImage.rootUrl }}{{ profile.profilePictureDisplayImage.artifacts[0].fileIdentifyingUrlPathSegment }}" />
        if profile.profilePicture is None and person.get('profilePictureDisplayImage') is not None:
            profile.profilePicture = person['profilePictureDisplayImage']['rootUrl'] + person['profilePictureDisplayImage']['artifacts'][0]['fileIdentifyingUrlPathSegment']
            profile.upsert()

    updated_profiles = LinkedInProfile.get_all()
    print(updated_profiles)



                # for profile in data.elements:
    #     if

    # for profile in data.elements:
    #     lip = LinkedInProfile(**profile)
    #     lip.upsert()
    #     print(lip.id)


