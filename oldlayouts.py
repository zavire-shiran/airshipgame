    def layout1(self):
        self.defaultlayout()
        for x in xrange(0, 12):
            self.addbuilding(Conveyor((x, 9), 'right'))
        for x in xrange(13, 24):
            self.addbuilding(Conveyor((x, 9), 'left'))
        for x in xrange(1,24,3):
            for y in xrange(0, 9):
                self.addbuilding(Extractor((x-1,y), 'right'))
                self.addbuilding(Conveyor((x,y), 'down'))
                self.addbuilding(Extractor((x+1,y), 'left'))
        for x in xrange(1,24,3):
            for y in xrange(10, 18):
                self.addbuilding(Extractor((x-1,y), 'right'))
                self.addbuilding(Conveyor((x,y), 'up'))
                self.addbuilding(Extractor((x+1,y), 'left'))
    def layout2(self):
        self.defaultlayout()
        for x in xrange(0, 12):
            self.addbuilding(Conveyor((x, 9), 'right'))
        for x in xrange(13, 24):
            self.addbuilding(Conveyor((x, 9), 'left'))
        for x in itertools.chain(xrange(0,7), xrange(18,24)):
            self.addbuilding(MultiExtractor((x,8), 'down'))
            self.addbuilding(MultiExtractor((x,10), 'up'))

        for y in xrange(0, 9):
            self.addbuilding(Conveyor((12,y), 'down'))
        for y in xrange(10, 18):
            self.addbuilding(Conveyor((12,y), 'up'))
        for y in itertools.chain(xrange(0, 7), xrange(12,18)):
            self.addbuilding(MultiExtractor((11,y), 'right'))
            self.addbuilding(MultiExtractor((13,y), 'left'))

        for x in xrange(7,11):
            self.addbuilding(Conveyor((x,8), 'right'))
            self.addbuilding(Conveyor((x,10), 'right'))
        self.addbuilding(Conveyor((7,7),'down'))
        self.addbuilding(Conveyor((6,7),'right'))
        self.addbuilding(Conveyor((7,11),'up'))
        self.addbuilding(Conveyor((6,11),'right'))
        for y in xrange(0,9):
            self.addbuilding(Conveyor((6,y), 'down'))
            self.addbuilding(MultiExtractor((5,y), 'right'))
            self.addbuilding(MultiExtractor((7,y), 'left'))
        for y in xrange(9,18):
            self.addbuilding(Conveyor((6,y), 'up'))
            self.addbuilding(MultiExtractor((5,y), 'right'))
            self.addbuilding(MultiExtractor((7,y), 'left'))

        for x in xrange(13,18):
            self.addbuilding(Conveyor((x,8), 'left'))
            self.addbuilding(Conveyor((x,10), 'left'))
        self.addbuilding(Conveyor((17,7),'down'))
        self.addbuilding(Conveyor((18,7),'left'))
        self.addbuilding(Conveyor((17,11),'up'))
        self.addbuilding(Conveyor((18,11),'left'))
        for y in xrange(0,9):
            self.addbuilding(Conveyor((18,y), 'down'))
            self.addbuilding(MultiExtractor((17,y), 'right'))
            self.addbuilding(MultiExtractor((19,y), 'left'))
        for y in xrange(9,18):
            self.addbuilding(Conveyor((18,y), 'up'))
            self.addbuilding(MultiExtractor((17,y), 'right'))
            self.addbuilding(MultiExtractor((19,y), 'left'))
            
        self.addbuilding(Conveyor((11,7),'down'))
        self.addbuilding(Conveyor((10,7),'right'))
        self.addbuilding(Conveyor((9,7),'right'))
        self.addbuilding(Conveyor((13,7),'down'))
        self.addbuilding(Conveyor((14,7),'left'))
        self.addbuilding(Conveyor((15,7),'left'))

        self.addbuilding(Conveyor((11,11),'up'))
        self.addbuilding(Conveyor((10,11),'right'))
        self.addbuilding(Conveyor((9,11),'right'))
        self.addbuilding(Conveyor((13,11),'up'))
        self.addbuilding(Conveyor((14,11),'left'))
        self.addbuilding(Conveyor((15,11),'left'))
        for y in xrange(0, 9):
            self.addbuilding(Conveyor((9,y), 'down'))
        for y in xrange(10, 18):
            self.addbuilding(Conveyor((9,y), 'up'))

        for y in xrange(0, 9):
            self.addbuilding(Conveyor((15,y), 'down'))
        for y in xrange(10, 18):
            self.addbuilding(Conveyor((15,y), 'up'))

        for y in xrange(0,18):
            self.addbuilding(MultiExtractor((8,y), 'right'))
            self.addbuilding(MultiExtractor((10,y), 'left'))
        for y in xrange(0,18):
            self.addbuilding(MultiExtractor((14,y), 'right'))
            self.addbuilding(MultiExtractor((16,y), 'left'))

    def layout3(self):
        self.defaultlayout()
        self.addbuilding(Factory((11,4), 'down'))
        self.addbuilding(Conveyor((12,7), 'down'))
        for x in xrange(0,11):
            self.addbuilding(Conveyor((x,4), 'right'))
            if x < 7:
                self.addbuilding(Extractor((x,5), 'up', ItemB))
                self.addbuilding(Extractor((x,3), 'down', ItemB))
        for x in xrange(14,24):
            self.addbuilding(Conveyor((x,4), 'left'))
            if x > 16:
                self.addbuilding(Extractor((x,5), 'up'))
                self.addbuilding(Extractor((x,3), 'down'))

        self.addbuilding(Factory((11,12), 'up'))
        self.addbuilding(Conveyor((12,11), 'up'))
        for x in xrange(0,11):
            self.addbuilding(Conveyor((x,14), 'right'))
            if x < 7:
                self.addbuilding(Extractor((x,15), 'up', ItemC))
                self.addbuilding(Extractor((x,13), 'down', ItemC))
        for x in xrange(14,24):
            self.addbuilding(Conveyor((x,14), 'left'))
            if x > 16:
                self.addbuilding(Extractor((x,15), 'up'))
                self.addbuilding(Extractor((x,13), 'down'))

        self.addbuilding(Factory((7,8), 'right'))
        self.addbuilding(Conveyor((10,9), 'right'))
        self.addbuilding(Conveyor((7,7), 'down'))
        self.addbuilding(Conveyor((7,11), 'up'))
        for x in xrange(0,7):
            self.addbuilding(Extractor((x,6), 'down', ItemB))
            self.addbuilding(Conveyor((x,7), 'right'))
            self.addbuilding(Extractor((x,8), 'up', ItemB))
            self.addbuilding(Extractor((x,10), 'down', ItemC))
            self.addbuilding(Conveyor((x,11), 'right'))
            self.addbuilding(Extractor((x,12), 'up', ItemC))

        self.addbuilding(Factory((15,8), 'left'))
        self.addbuilding(Conveyor((14,9), 'left'))
        self.addbuilding(Conveyor((17,7), 'down'))
        self.addbuilding(Conveyor((17,11), 'up'))
        for x in xrange(17,24):
            self.addbuilding(MultiExtractor((x,6), 'down'))
            self.addbuilding(Conveyor((x,7), 'left'))
            self.addbuilding(MultiExtractor((x,8), 'up'))
            self.addbuilding(MultiExtractor((x,10), 'down'))
            self.addbuilding(Conveyor((x,11), 'left'))
            self.addbuilding(MultiExtractor((x,12), 'up'))
