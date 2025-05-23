import unittest


__copyright__ = "Copyright 2024, Netflix, Inc."
__license__ = "BSD+Patent"

from vmaf.tools.bd_rate import calculate_bd_rate
from vmaf.tools.exceptions import BdRateNonMonotonicException, \
    BdRateNoOverlapException
from vmaf.tools.typing_utils import RdPoint


def create_rd_points(data: list[tuple[float, float]]) -> list[RdPoint]:
    return [RdPoint(rate=rate, metric=metric) for rate, metric in data]


class CalculateBdRateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.set_a = create_rd_points(
            [
                (35.99646889759373, 21.955645250419696),
                (37.99471487409067, 25.51236452853944),
                (39.970621712367105, 28.044365039171787),
                (42.346972697257975, 30.479270893956333),
                (44.7457131337437, 32.55129509653048),
                (47.154365304980416, 34.35170492445439),
                (49.85285605484052, 36.159880512031336),
                (52.668811762730826, 37.817858687744824),
                (55.623246648013435, 39.4236739227756),
                (58.709821225517615, 40.97726075825405),
                (61.95339030218243, 42.47586071628426),
                (65.39086712367096, 43.94792672076104),
                (69.07053575825405, 45.38187315332959),
                (72.92296374930051, 46.7512838066592),
                (77.04220356463348, 48.12043552042529),
                (81.27714736989365, 49.42854125629547),
                (85.80023587017347, 50.72125632344712),
                (90.70151323447116, 52.02140726776721),
                (95.61377568550643, 53.247009597090084),
                (101.18490854504753, 54.54781877448235),
                (106.70571125909345, 55.77207227895914),
                (112.80107593732511, 57.05675384023505),
                (118.71002956351424, 58.22286424174595),
                (125.49624718522664, 59.4644650601567),
                (132.55080280358143, 60.67429805540012),
                (140.1958864969222, 61.90510035674314),
                (147.88641993844433, 63.041928063794046),
                (156.33494113598206, 64.22106624930048),
                (164.76788195858984, 65.33567544767766),
                (173.94668501398993, 66.48116736149971),
                (184.07738357022944, 67.64570549104643),
                (194.3000549748181, 68.7236593242865),
                (205.02014116955786, 69.79909077364297),
                (216.48558646334627, 70.86179997202017),
                (228.6963740850587, 71.91020905148292),
                (241.1654202574147, 72.91811104504754),
                (254.97357365976498, 73.96942905008393),
                (269.34394547845557, 74.9730472439843),
                (284.15034977056513, 75.93786445159483),
                (300.33591073866813, 76.91376459149411),
                (317.0971573363177, 77.86057887520982),
                (334.6360977616115, 78.78165542809175),
                (353.52509696138776, 79.69565129406824),
                (373.29134338556247, 80.57908869613874),
                (393.9552307218803, 81.44409020705092),
                (415.95752090095135, 82.30904120733068),
                (438.74847322327906, 83.13002760212642),
                (463.7617672915498, 83.97161655008395),
                (490.0063805707889, 84.77690864577501),
                (516.9553140067148, 85.5381991116396),
                (544.9439733240066, 86.28044596390599),
                (576.3607511751537, 87.049304036094),
                (607.7912813486286, 87.75004198377168),
                (642.9993396698372, 88.46859445998881),
                (678.4288774650249, 89.13938649272522),
                (716.0146116899828, 89.79232830861778),
                (757.1422397593731, 90.43804418019025),
                (799.5379996586456, 91.04304998601005),
                (843.7057127476214, 91.61936168158924),
                (891.0241835086737, 92.18129753777283),
                (941.0654296082818, 92.7274914871293),
                (992.0100858869608, 93.22531138080583),
                (1049.361345377728, 93.72490778539446),
                (1106.0225737101287, 94.16627750419697),
                (1169.031521835478, 94.61364252937885),
                (1234.2873478623392, 95.02554775461667),
                (1303.8650088919974, 95.42153838836039),
                (1377.1698176105203, 95.788557491606),
                (1453.2463230386118, 96.12595161583663),
                (1532.4943320201453, 96.43917551762732),
                (1621.3588033296023, 96.747294998601),
                (1705.825332271964, 97.00223929071069),
                (1807.3925386066035, 97.27276210128707),
                (1908.5000484107447, 97.50972255875773),
                (2014.398598975937, 97.72906203133745),
                (2127.9466272691657, 97.92876842473417),
                (2245.784021667598, 98.10873614297704),
                (2371.8831237045324, 98.2783919418019),
                (2505.2980083995526, 98.43403286233912),
                (2644.597092540571, 98.57010871572473),
                (2790.9417932904316, 98.69238183407946),
                (2948.672410660327, 98.80515458869611),
                (3107.1893589871306, 98.90337104085056),
                (3288.155564739787, 98.99696463346388),
                (3470.8710826636825, 99.07321914521543),
                (3665.2945898880803, 99.14012702853941),
                (3869.5733634862895, 99.19701270285395),
                (4071.5218731505315, 99.24300500839394),
                (4311.484267084497, 99.28674711807501),
                (4558.244802909904, 99.31946469641859),
                (4806.482321382206, 99.34378444320092),
                (5079.722132064913, 99.36144804141017),
                (5361.911769636264, 99.37290286793508),
                (5665.047368091774, 99.38022224398433),
                (5973.631636653609, 99.38404458589815),
                (6315.611591936206, 99.38606273782877),
                (6667.651857364297, 99.3870162283156),
                (7037.4516035086735, 99.3875896334639),
                (7434.023280637938, 99.38792124370454),
            ]
        )

    def test_calculate_bd_rate_identical(self) -> None:
        bd_rate = calculate_bd_rate(self.set_a, self.set_a)
        expected_bd_rate = 0.0
        self.assertAlmostEqual(expected_bd_rate, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, self.set_a, at_perc=100)
        expected_bd_rate = 0.0
        self.assertAlmostEqual(expected_bd_rate, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, self.set_a, at_perc=50)
        expected_bd_rate = 0.0
        self.assertAlmostEqual(expected_bd_rate, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, self.set_a, at_perc=0)
        expected_bd_rate = 0.0
        self.assertAlmostEqual(expected_bd_rate, bd_rate, places=8)

    def test_calculate_bd_rate_different_slightly(self) -> None:
        set_b = create_rd_points(
            [
                (35.99646889759373, 21.955645250419696),
                (37.99471487409067, 25.51236452853944),
                (39.970621712367105, 28.044365039171787),
                (42.346972697257975, 30.479270893956333),
                (44.7457131337437, 32.55129509653048),
                (47.154365304980416, 34.35170492445439),
                (49.85285605484052, 36.159880512031336),
                (52.668811762730826, 37.817858687744824),
                (55.623246648013435, 39.4236739227756),
                (58.709821225517615, 40.97726075825405),
                (61.95339030218243, 42.47586071628426),
                (65.39086712367096, 43.94792672076104),
                (69.07053575825405, 45.38187315332959),
                (72.92296374930051, 46.7512838066592),
                (77.04220356463348, 48.12043552042529),
                (81.26477027979853, 49.42465443480694),
                (85.78785878007832, 50.71736950195859),
                (90.68913614437604, 52.017520446278674),
                (95.6013985954113, 53.24312277560156),
                (101.1049438220481, 54.528708883603784),
                (106.72526639059875, 55.77544413122552),
                (112.82063106883044, 57.06012569250141),
                (118.72958469501955, 58.22623609401232),
                (125.51580231673195, 59.46783691242307),
                (132.55080280358143, 60.67429805540012),
                (140.1958864969222, 61.90510035674314),
                (147.88641993844433, 63.041928063794046),
                (156.33494113598206, 64.22106624930048),
                (164.76788195858984, 65.33567544767766),
                (173.94668501398993, 66.48116736149971),
                (184.07738357022944, 67.64570549104643),
                (194.3000549748181, 68.7236593242865),
                (205.02014116955786, 69.79909077364297),
                (216.48558646334627, 70.86179997202017),
                (228.6963740850587, 71.91020905148292),
                (241.1654202574147, 72.91811104504754),
                (254.97357365976498, 73.96942905008393),
                (269.34394547845557, 74.9730472439843),
                (284.15034977056513, 75.93786445159483),
                (300.33591073866813, 76.91376459149411),
                (317.0971573363177, 77.86057887520982),
                (334.6360977616115, 78.78165542809175),
                (353.52509696138776, 79.69565129406824),
                (373.29134338556247, 80.57908869613874),
                (393.9552307218803, 81.44409020705092),
                (415.95752090095135, 82.30904120733068),
                (438.74847322327906, 83.13002760212642),
                (463.7617672915498, 83.97161655008395),
                (489.84063154448785, 84.77202437045325),
                (516.7895649804138, 85.53331483631784),
                (544.9749663626188, 86.28081538192502),
                (576.8655284890876, 87.06078310016787),
                (607.6881892445435, 87.74725560996083),
                (642.8791074762167, 88.46546687185227),
                (678.3086452714043, 89.13625890458867),
                (715.8616087185223, 89.78865049664242),
                (757.1041860772242, 90.435000188864),
                (798.15463343033, 91.02080761052042),
                (843.5981930665919, 91.61538377867933),
                (890.6553361611639, 92.17446489927256),
                (941.2275728427528, 92.72510695299388),
                (991.9775666759929, 93.22055148992727),
                (1049.150817448237, 93.71790935926131),
                (1105.4788035310573, 94.15517948377166),
                (1169.7203790151086, 94.61349013010631),
                (1235.467531913822, 95.02758209988808),
                (1303.7973206323445, 95.41458729015112),
                (1375.6589572915498, 95.77265730973697),
                (1454.1877533575819, 96.1213997341914),
                (1535.3317379966425, 96.43969173894797),
                (1619.041704728595, 96.72884599188583),
                (1706.2542370173471, 96.9918582470621),
                (1806.7879060156686, 97.25875356043645),
                (1907.8936883939557, 97.4924479854505),
                (2012.3483121992158, 97.70996307358699),
                (2126.4842019585894, 97.90953160324563),
                (2245.182894241745, 98.08930167879124),
                (2370.2106903693343, 98.25233185506434),
                (2500.319466463347, 98.3971445928931),
                (2643.4560019809737, 98.52912282456631),
                (2778.632123116957, 98.63288324006716),
                (2948.7437885674317, 98.738307113878),
                (3109.8279768214884, 98.81400232232791),
                (3278.805042137661, 98.8647137101287),
            ]
        )

        bd_rate = calculate_bd_rate(self.set_a, set_b)
        expected_bd_rate = 0.000537973253591284
        self.assertAlmostEqual(expected_bd_rate, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=100)
        expected_bd_rate = 0.07795646560507974
        self.assertAlmostEqual(expected_bd_rate, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=50)
        expected_bd_rate = 4.613748580961641e-07
        self.assertAlmostEqual(expected_bd_rate, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=0)
        expected_bd_rate = 0.0
        self.assertAlmostEqual(expected_bd_rate, bd_rate, places=8)

    def test_calculate_bd_rate_different(self) -> None:
        set_b = create_rd_points(
            [
                (49.87328328483493, 28.61330510632344),
                (52.38326659205375, 32.39771999160604),
                (55.48787012870734, 35.43877945579183),
                (58.73340142697256, 37.81863505176273),
                (61.38781766088415, 39.45287702853945),
                (65.24973810856183, 41.51289594991606),
                (68.91803592053719, 43.25002306939003),
                (72.90461613878006, 44.95657251678791),
                (76.50681894795746, 46.343293172915494),
                (81.22743775601566, 48.06086461947399),
                (85.8963679574706, 49.55961627728036),
                (90.6221019585898, 50.90070572887522),
                (95.65390898712923, 52.23381047146056),
                (101.13434360380525, 53.61339359960829),
                (106.40240546726353, 54.8475233841634),
                (112.42335666480132, 56.18486674594291),
                (118.79365039171795, 57.459968270844996),
                (125.05231551203133, 58.63419768466705),
                (132.43335461667598, 59.89586900531618),
                (139.88996440962507, 61.0835185996083),
                (146.16949280917734, 62.04168247761612),
                (155.7417632232793, 63.3899363878008),
                (163.313640956911, 64.36612914101849),
                (173.5439432232792, 65.58913973139342),
                (182.53828067711245, 66.58945198656969),
                (193.15859545047564, 67.70600593172915),
                (204.38533732512593, 68.81500302182431),
                (215.95536735310577, 69.90734120033578),
                (227.63617066032455, 70.90756786513711),
                (241.31498514829323, 71.9597451385003),
                (253.7268753273643, 72.82036908925575),
                (267.2595965472859, 73.70446921516509),
                (283.9250800223839, 74.66681882344713),
                (294.27475915500827, 75.23454667039732),
                (316.458982495803, 76.38518377867935),
                (334.1048723838837, 77.20506813094572),
                (352.4061945998881, 77.96106693480695),
                (369.71439789031893, 78.57269429910465),
                (388.71730656966986, 79.09373393956353),
                (416.22584212646893, 79.73839594292109),
                (431.8296127756015, 80.04573062395076),
                (456.8111591046446, 80.4380911723559),
                (489.9550944711808, 80.81746619334079),
                (505.8411566927812, 80.9060061345831),
                (531.839469233352, 81.04617807078903),
            ]
        )

        bd_rate = calculate_bd_rate(self.set_a, set_b)
        self.assertAlmostEqual(0.0828609163164793, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=100)
        self.assertAlmostEqual(0.38396884941389553, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=50)
        self.assertAlmostEqual(0.03800171560649668, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=0)
        self.assertAlmostEqual(0.23201845983320446, bd_rate, places=8)

    def test_calculate_bd_rate_nonoverlap(self) -> None:
        set_b = create_rd_points([(point.rate, point.metric + 100.0) for point in self.set_a])
        self.assertRaises(BdRateNoOverlapException, calculate_bd_rate, self.set_a, set_b)

    def test_calculate_bd_rate_proportional(self) -> None:
        set_b = create_rd_points([(point.rate * 1.1, point.metric) for point in self.set_a])

        bd_rate = calculate_bd_rate(self.set_a, set_b)
        self.assertAlmostEqual(0.1, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=100)
        self.assertAlmostEqual(0.1, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=50)
        self.assertAlmostEqual(0.1, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=0)
        self.assertAlmostEqual(0.1, bd_rate, places=8)

    def test_calculate_bd_rate_proportional2(self) -> None:
        set_b = create_rd_points([(point.rate * 0.9, point.metric) for point in self.set_a])

        bd_rate = calculate_bd_rate(self.set_a, set_b)
        self.assertAlmostEqual(-0.1, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=100)
        self.assertAlmostEqual(-0.1, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=50)
        self.assertAlmostEqual(-0.1, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=0)
        self.assertAlmostEqual(-0.1, bd_rate, places=8)

    def test_calculate_bd_rate_constant(self) -> None:
        set_b = create_rd_points([(point.rate + 100.0, point.metric) for point in self.set_a])

        bd_rate = calculate_bd_rate(self.set_a, set_b)
        self.assertAlmostEqual(0.8570879677536116, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=100)
        # 7534.023280637938 / 7434.023280637938 - 1 = 0.01345166624113947
        self.assertAlmostEqual(0.01345166624113947, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=50)
        self.assertAlmostEqual(0.7545138350290654, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=0)
        # 135.99646889759373 / 35.99646889759373 - 1 = 2.778050266110539
        self.assertAlmostEqual(2.778050266110539, bd_rate, places=8)

    def test_calculate_bd_rate_constant2(self) -> None:
        set_b = create_rd_points([(point.rate - 10.0, point.metric) for point in self.set_a])

        bd_rate = calculate_bd_rate(self.set_a, set_b)
        self.assertAlmostEqual(-0.10612811471545303, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=100)
        self.assertAlmostEqual(-0.0013451666241135474, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=50)
        self.assertAlmostEqual(-0.07545138577059218, bd_rate, places=8)

        bd_rate = calculate_bd_rate(self.set_a, set_b, at_perc=0)
        self.assertAlmostEqual(-0.277805026611054, bd_rate, places=8)


class CalculateBdRateJCTVCTest(unittest.TestCase):
    def test_calculate_bd_rate_1(self) -> None:
        score = calculate_bd_rate(
            create_rd_points([(108048.8736, 43.6471), (61279.976, 40.3953), (33905.6656, 37.247), (18883.6928, 34.2911)]),
            create_rd_points([(108061.2784, 43.6768), (61299.9936, 40.4232), (33928.7472, 37.2761), (18910.912, 34.3147)]),
        )
        expected_score = -0.00465215420752807
        self.assertAlmostEqual(expected_score, score, places=4)

    def test_calculate_bd_rate_2(self) -> None:
        score = calculate_bd_rate(
            create_rd_points([(40433.8848, 37.5761), (7622.7456, 35.3756), (2394.488, 33.8977), (1017.6184, 32.0603)]),
            create_rd_points([(40370.12, 37.5982), (7587.0024, 35.4025), (2390.0944, 33.9194), (1017.0984, 32.0822)]),
        )
        expected_score = -0.018779823450567612
        self.assertAlmostEqual(expected_score, score, places=4)

    def test_calculate_bd_rate_non_monotonic(self) -> None:
        with self.assertRaises(BdRateNonMonotonicException):
            _ = calculate_bd_rate(
                create_rd_points([(108048.8736, 39.6471), (61279.976, 40.3953), (33905.6656, 37.247), (18883.6928, 34.2911)]),
                create_rd_points([(108061.2784, 43.6768), (61299.9936, 40.4232), (33928.7472, 37.2761), (18910.912, 34.3147)]),
            )

    def test_calculate_bd_rate_non_monotonic2(self) -> None:
        with self.assertRaises(BdRateNonMonotonicException):
            _ = calculate_bd_rate(
                create_rd_points([(58048.8736, 43.6471), (61279.976, 40.3953), (33905.6656, 37.247), (18883.6928, 34.2911)]),
                create_rd_points([(108061.2784, 43.6768), (61299.9936, 40.4232), (33928.7472, 37.2761), (18910.912, 34.3147)]),
            )


if __name__ == "__main__":
    unittest.main()
