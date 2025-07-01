# from django.core.management.base import BaseCommand
# from admin_pannel.models import Country, State, City, Branch


# class Command(BaseCommand):
#     help = 'Populate countries, states, cities, and branches for India'

#     def handle(self, *args, **kwargs):
#         india, _ = Country.objects.get_or_create(name='India')

#         states = {
#             'Andhra Pradesh': india,
#             'Telangana': india,
#             'Karnataka': india,
#             'Tamil Nadu': india,
#             'Madhya Pradesh': india,
#             'West Bengal': india,
#             'Uttar Pradesh': india,
#             'Maharashtra': india,
#         }

#         state_objs = {}
#         for state_name, country in states.items():
#             state_obj, _ = State.objects.get_or_create(name=state_name, country=country)
#             state_objs[state_name] = state_obj

#         city_state_map = {
#             'Hyderabad': 'Telangana',
#             'Warangal': 'Telangana',
#             'Vijayawada': 'Andhra Pradesh',
#             'Guntur': 'Andhra Pradesh',
#             'Visakhapatnam': 'Andhra Pradesh',
#             'Bangalore': 'Karnataka',
#             'Mysore': 'Karnataka',
#             'Chennai': 'Tamil Nadu',
#             'Madurai': 'Tamil Nadu',
#             'Coimbatore': 'Tamil Nadu',
#             'Bhopal': 'Madhya Pradesh',
#             'Indore': 'Madhya Pradesh',
#             'Kolkata': 'West Bengal',
#             'Lucknow': 'Uttar Pradesh',
#             'Kanpur': 'Uttar Pradesh',
#             'Noida': 'Uttar Pradesh',
#             'Mumbai': 'Maharashtra',
#             'Pune': 'Maharashtra',
#             'Nagpur': 'Maharashtra',
#         }

#         city_area_map = {
#             'Hyderabad': ['Kukatpally', 'Hitech City', 'Ameerpet', 'Gachibowli', 'Mehdipatnam'],
#             'Vijayawada': ['Benz Circle', 'Governorpet', 'Kanuru', 'Auto Nagar', 'Poranki'],
#             'Visakhapatnam': ['MVP Colony', 'Gajuwaka', 'Dwaraka Nagar', 'Seethammadhara', 'Rushikonda'],
#             'Bangalore': ['Whitefield', 'Indiranagar', 'Koramangala', 'Electronic City', 'Jayanagar'],
#             'Chennai': ['T. Nagar', 'Velachery', 'Guindy', 'Anna Nagar', 'Adyar'],
#             'Mumbai': ['Andheri', 'Borivali', 'Bandra', 'Dadar', 'Vikhroli'],
#             'Pune': ['Hinjewadi', 'Kothrud', 'Wakad', 'Viman Nagar', 'Baner'],
#             'Kolkata': ['Salt Lake', 'Garia', 'Howrah', 'Behala', 'Dumdum'],
#             'Lucknow': ['Hazratganj', 'Aliganj', 'Gomti Nagar', 'Indira Nagar', 'Chowk'],
#             'Bhopal': ['Arera Colony', 'TT Nagar', 'Kolar', 'Shahpura', 'MP Nagar'],
#             'Coimbatore': ['Peelamedu', 'Gandhipuram', 'RS Puram', 'Ukkadam', 'Town Hall'],
#             'Indore': ['Vijay Nagar', 'Rajwada', 'Palasia', 'MG Road', 'Sudama Nagar'],
#             'Warangal': ['Hanamkonda', 'Kazipet', 'Subedari', 'Narsampet Road', 'Station Ghanpur'],
#             'Mysore': ['VV Mohalla', 'Jayalakshmipuram', 'Kuvempunagar', 'Saraswathipuram', 'Lashkar Mohalla'],
#             'Madurai': ['KK Nagar', 'Anna Nagar', 'Thiruppalai', 'Tallakulam', 'Goripalayam'],
#             'Noida': ['Sector 62', 'Sector 18', 'Sector 137', 'Sector 15', 'Sector 50'],
#             'Nagpur': ['Dharampeth', 'Sitabuldi', 'Wardha Road', 'Mahal', 'Civil Lines'],
#             'Kanpur': ['Swaroop Nagar', 'Kakadeo', 'Shastri Nagar', 'Govind Nagar', 'Ratan Lal Nagar'],
#             'Guntur': ['Brodipet', 'Arundelpet', 'Nallapadu', 'Sunnapubattilu', 'Nallacheruvu'],
#         }

#         for city_name, areas in city_area_map.items():
#             state_name = city_state_map.get(city_name)
#             if not state_name:
#                 self.stdout.write(self.style.WARNING(f"State not found for city '{city_name}'. Skipping."))
#                 continue

#             state = state_objs.get(state_name)
#             if not state:
#                 self.stdout.write(self.style.WARNING(f"State object for '{state_name}' not found. Skipping city '{city_name}'."))
#                 continue

#             city, _ = City.objects.get_or_create(name=city_name, state=state)

#             for area in areas:
#                 branch, created = Branch.objects.get_or_create(name=area, city=city)
#                 if created:
#                     self.stdout.write(self.style.SUCCESS(f"Created branch '{area}' in city '{city_name}'"))
from django.core.management.base import BaseCommand
from admin_pannel.models import Country, State, City, Branch

class Command(BaseCommand):
    help = 'Populate countries, states, cities, and branches for multiple countries'

    def handle(self, *args, **kwargs):
        country_data = {
            'India': {
                'Telangana': {
                    'Hyderabad': ['Kukatpally', 'Gachibowli', 'Ameerpet', 'Mehdipatnam', 'Secunderabad'],
                    'Warangal': ['Kazipet', 'Hanamkonda', 'Subedari'],
                    
                },
                'Karnataka': {
                    'Bangalore': ['Whitefield', 'Koramangala', 'Indiranagar'],
                    'Mysore': ['VV Mohalla', 'Jayalakshmipuram']
                },
                
            },
            'USA': {
                'California': {
                    'Los Angeles': ['Hollywood', 'Beverly Hills', 'Downtown'],
                    'San Francisco': ['Mission District', 'Chinatown', 'Fisherman’s Wharf']
                },
                'Texas': {
                    'Austin': ['Downtown', 'Zilker', 'Hyde Park'],
                    'Dallas': ['Deep Ellum', 'Bishop Arts', 'Uptown']
                }
            },
            'UK': {
                'England': {
                    'London': ['Chelsea', 'Camden', 'Greenwich', 'Stratford'],
                    'Manchester': ['Didsbury', 'Chorlton', 'Ancoats']
                },
                'Scotland': {
                    'Edinburgh': ['Leith', 'Old Town', 'New Town'],
                    'Glasgow': ['Partick', 'Shawlands', 'Merchant City']
                }
            },
            'Canada': {
                'Ontario': {
                    'Toronto': ['Downtown', 'North York', 'Scarborough'],
                    'Ottawa': ['Kanata', 'Nepean', 'Orleans']
                },
                'British Columbia': {
                    'Vancouver': ['Downtown', 'Kitsilano', 'Burnaby'],
                    'Victoria': ['James Bay', 'Oak Bay', 'Downtown']
                }
            },
            'Australia': {
                'New South Wales': {
                    'Sydney': ['Parramatta', 'Bondi', 'Newtown'],
                    'Newcastle': ['Hamilton', 'Merewether', 'Wallsend']
                },
                'Victoria': {
                    'Melbourne': ['CBD', 'St Kilda', 'Carlton'],
                    'Geelong': ['Belmont', 'Highton', 'Newtown']
                }
            }
        }

        for country_name, states in country_data.items():
            country, _ = Country.objects.get_or_create(name=country_name)
            self.stdout.write(self.style.SUCCESS(f"Processing country: {country_name}"))

            for state_name, cities in states.items():
                state, _ = State.objects.get_or_create(name=state_name, country=country)
                self.stdout.write(self.style.SUCCESS(f"  State: {state_name}"))

                for city_name, branches in cities.items():
                    city, _ = City.objects.get_or_create(name=city_name, state=state)
                    self.stdout.write(self.style.SUCCESS(f"    City: {city_name}"))

                    for branch_name in branches:
                        branch, created = Branch.objects.get_or_create(name=branch_name, city=city)
                        if created:
                            self.stdout.write(self.style.SUCCESS(f"      Branch Created: {branch_name}"))

