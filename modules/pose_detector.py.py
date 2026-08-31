import cv2
import mediapipe as mp
import time

class PoseDetector():
    def  __init__(self, mode=False, model_complexity=1, smooth=True, detectionCon=0.5, trackCon=0.5):

        self.mode = mode
        self.model_complexity = model_complexity
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            static_image_mode=self.mode,
            model_complexity=self.model_complexity,
            smooth_landmarks=self.smooth,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)

        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(
                img, self.results.pose_landmarks,
                self.mpPose.POSE_CONNECTIONS,
                self.mpDraw.DrawingSpec(color=(0,0 , 220), thickness=2, circle_radius=4),
                self.mpDraw.DrawingSpec(color=(0, 250, 0), thickness=2)
                )
        return img            
            
    def findPosition(self, img, draw=True):
        if self.results.pose_landmarks:
            lmList = []
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                lmList.append([id, cx,cy])
                if draw:
                    cv2.circle(img, (cx,cy), 5, (0,0,255), cv2.FILLED) 
        return lmList            

def main():
    cap = cv2.VideoCapture("video/ayan.mp4")
    cTime = 0
    pTime = 0
    detector = PoseDetector()
    while True:
        success, img = cap.read()
        if not success:
            print("Video load nahi hui - path check karo")
            break
        img = detector.findPose(img)
        lmList = detector.findPosition(img)
        if lmList != 0:
            print(lmList)
            cv2.circle(img, (lmList[14][1],lmList[12][1]), 15, (0,0,255), cv2.FILLED) 

        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (70,50), cv2.FONT_HERSHEY_PLAIN, 3,  (255,0,0), 3 )
        cv2.imshow("Image",img)
        
        
        cv2.waitKey(1)



if __name__ == "__main__":
    main()