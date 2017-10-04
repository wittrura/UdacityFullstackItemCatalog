from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup_postgres import Base, Genre, Manga, User

engine = create_engine('postgresql://catalog:udacity@localhost:5432/catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()



User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


genre1 = Genre(name="Action", user_id = 1)
session.add(genre1)
session.commit()


genre2 = Genre(name="Psychological", user_id = 1)
session.add(genre2)
session.commit()


genre3 = Genre(name="Shounen", user_id = 1)
session.add(genre3)
session.commit()


genre4 = Genre(name="Harem", user_id = 1)
session.add(genre4)
session.commit()


genre5 = Genre(name="Seinen", user_id = 1)
session.add(genre5)
session.commit()



mangaItem1 = Manga(name="Naruto",
                volumes = 72,
                chapters = 700,
                description="Before Naruto's birth, a great demon fox had attacked the Hidden Leaf Village. A man known as the 4th Hokage sealed the demon inside the newly born Naruto, causing him to unknowingly grow up detested by his fellow villagers. Despite his lack of talent in many areas of ninjutsu, Naruto strives for only one goal: to gain the title of Hokage, the strongest ninja in his village. Desiring the respect he never received, Naruto works toward his dream with fellow friends Sasuke and Sakura and mentor Kakashi as they go through many trials and battles that come with being a ninja",
                authors = "Kishimoto, Masashi",
                user_id = 1,
                genre=genre1)

session.add(mangaItem1)
session.commit()


mangaItem2 = Manga(name="Bleach",
                volumes = 74,
                chapters = 705,
                description="Ichigo Kurosaki has always been able to see ghosts, but this ability doesn't change his life nearly as much as his close encounter with Rukia Kuchiki, a Soul Reaper and member of the mysterious Soul Society. While fighting a Hollow, an evil spirit that preys on humans who display psychic energy, Rukia attempts to lend Ichigo some of her powers so that he can save his family; but much to her surprise, Ichigo absorbs every last drop of her energy. Now a full-fledged Soul Reaper himself, Ichigo quickly learns that the world he inhabits is one full of dangerous spirits and, along with Rukia - who is slowly regaining her powers - it's Ichigo's job to protect the innocent from Hollows and help the spirits themselves find peace.",
                authors = "Kubo, Tite",
                user_id = 1,
                genre=genre1)

session.add(mangaItem2)
session.commit()


mangaItem3 = Manga(name="Fairy Tail",
                volumes = 63,
                chapters = 549,
                description="In the mystical realm of Earth Land, magic exists at the core of everyday life for its inhabitants, from transportation to utilities and everything in between. However, even with all its benefits, magic can also be used for great evil; therefore, to prevent dark forces from upsetting the natural order of things, there exists a system of magical guilds in the Kingdom of Fiore. Under the command of their respective guild masters, these guilds are made up of witches and wizards who take on various job requests to earn fame and fortune. One particular guild stands high above the rest in both strength and spirit, and its name is Fairy Tail.",
                authors = "Mashima, Hiro",
                user_id = 1,
                genre=genre1)

session.add(mangaItem3)
session.commit()


mangaItem4 = Manga(name="Tokyo Ghoul",
                volumes = 14,
                chapters = 144,
                description='Lurking within the shadows of Tokyo are frightening beings known as "ghouls," who satisfy their hunger by feeding on humans once night falls. An organization known as the Commission of Counter Ghoul (CCG) has been established in response to the constant attacks on citizens and as a means of purging these creatures. However, the problem lies in identifying ghouls as they disguise themselves as humans, living amongst the masses so that hunting prey will be easier. Ken Kaneki, an unsuspecting university freshman, finds himself caught in a world between humans and ghouls when his date turns out to be a ghoul after his flesh.',
                authors = "Mashima, Hiro",
                user_id = 1,
                genre=genre5)

session.add(mangaItem4)
session.commit()


mangaItem5 = Manga(name="Berserk",
                volumes = 50,
                chapters = 430,
                description='Guts, a former mercenary now known as the "Black Swordsman," is out for revenge. After a tumultuous childhood, he finally finds someone he respects and believes he can trust, only to have everything fall apart when this person takes away everything important to Guts for the purpose of fulfilling his own desires. Now marked for death, Guts becomes condemned to a fate in which he is relentlessly pursued by demonic beings.',
                authors = "Miura, Kentarou",
                user_id = 1,
                genre=genre5)

session.add(mangaItem5)
session.commit()


mangaItem6 = Manga(name="Shingeki no Kyojin",
                volumes = 15,
                chapters = 95,
                description="Hundreds of years ago, horrifying creatures which resembled humans appeared. These mindless, towering giants, called 'titans,' proved to be an existential threat, as they preyed on whatever humans they could find in order to satisfy a seemingly unending appetite. Unable to effectively combat the titans, mankind was forced to barricade themselves within large walls surrounding what may very well be humanity's last safe haven in the world.",
                authors = "Isayama, Hajime",
                user_id = 1,
                genre=genre3)

session.add(mangaItem6)
session.commit()


mangaItem7 = Manga(name="Death Note",
                volumes = 12,
                chapters = 108,
                description="A shinigami, as a god of death, can kill any person - provided they see their victim's face and write their victim's name in a notebook called a Death Note. One day, Ryuk, bored by the shinigami lifestyle and interested in seeing how a human would use a Death Note, drops one into the human realm.",
                authors = "Obata, Takeshi (Art), Ohba, Tsugumi (Story)",
                user_id = 1,
                genre=genre3)

session.add(mangaItem7)
session.commit()


mangaItem8 = Manga(name="Rosario to Vampire",
                volumes = 10,
                chapters = 40,
                description="Aono Tsukune is so hard up on luck, that he can't even get admitted into high school. His parents finally find him a school with no tests required for admittance, out in the middle of nowhere. He finds out the school is a youkai (monster) academy, Just as he is about to resign himself and get back on the bus home, he bumps into a beautiful girl. Turns out this beautiful girl, Akashiya Moka, is also a vampire who bites him right off the bat. They become friends and Tsukune is ready for a happy school life with her, until he finds out that if a human is found on the school grounds, he or she should be killed.",
                authors = "Ikeda, Akihisa",
                user_id = 1,
                genre=genre4)

session.add(mangaItem8)
session.commit()


mangaItem9 = Manga(name="Elfen Lied",
                volumes = 12,
                chapters = 113,
                description="Lucy is a special breed of human referred to as 'Diclonius,' born with a short pair of horns and invisible telekinetic hands that lands her as a victim of inhumane scientific experimentation by the government. However, once circumstances present her an opportunity to escape, Lucy, corrupted by the confinement and torture, unleashes a torrent of bloodshed as she escapes her captors.",
                authors = "Okamoto, Lynn",
                user_id = 1,
                genre=genre2)

session.add(mangaItem9)
session.commit()

print "added genre and manga items!"
