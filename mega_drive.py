from mega import Mega

#create instance of mega
mega = Mega()

email = "nitesh@dowellresearch.in"
password = "RstuKnA*u9"


m = mega.login(email,password)
#login using temporary anonymous account
#m = mega.login()

details = m.get_user()


balance = m.get_balance()


quota = m.get_quota()


space = m.get_storage_space(kilo=True)
print(space)

#files = m.get_files()

#print(files)

# name = str('MY_SEO')
# m.create_folder(name)

print("-------")

folder = m.find('social_media_images')


file = m.upload('flower.jpg',folder[0])

m.download('flower1.jpg')
m.download('flower2.jpg')

file_link = m.get_upload_link(file)

print(file_link)

print(m.root_id)

#print(m.find_path_descriptor("Go0kbqQ"))




