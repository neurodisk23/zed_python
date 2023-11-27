import cv2
import numpy
import pyzed.sl as sl
inter = cv2.INTER_AREA


def main() :

    # Create a ZED camera object
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    init_params.coordinate_units = sl.UNIT.METER
    init_params.sdk_verbose = 1

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS :
        print(repr(err))
        zed.close()
        exit(1)

    # Display help in console
  

    # Set runtime parameters after opening the camera
    runtime = sl.RuntimeParameters()

    # Prepare new image size to retrieve half-resolution images
    image_size = zed.get_camera_information().camera_configuration.resolution
    image_size.width = image_size.width /2
    image_size.height = image_size.height /2

    # Declare your sl.Mat matrices
    image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
    depth_image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
    point_cloud = sl.Mat()





    obj_param = sl.ObjectDetectionParameters()
    obj_param.enable_tracking=True
    obj_param.enable_segmentation=True
    obj_param.detection_model = sl.OBJECT_DETECTION_MODEL.MULTI_CLASS_BOX_MEDIUM

    if obj_param.enable_tracking :
        positional_tracking_param = sl.PositionalTrackingParameters()
        #positional_tracking_param.set_as_static = True
        zed.enable_positional_tracking(positional_tracking_param)

    print("Object Detection: Loading Module...")

    err = zed.enable_object_detection(obj_param)
    if err != sl.ERROR_CODE.SUCCESS :
        print("Enable object detection : "+repr(err)+". Exit program.")
        zed.close()
        exit()

    objects = sl.Objects()
    obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
    obj_runtime_param.detection_confidence_threshold = 40











    key = ' '
    while key != 113 :
        err = zed.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS :
            zed.grab()
            zed.retrieve_objects(objects,obj_runtime_param)
            if objects.is_new :
                obj_array = objects.object_list
                print(str(len(obj_array))+" Object(s) detected\n")
                if len(obj_array) > 0 :
                    first_object = obj_array[0]
                    print("First object attributes:")
                    print(" Label '"+repr(first_object.label)+"' (conf. "+str(int(first_object.confidence))+"/100)")
                    if obj_param.enable_tracking :
                        print(" Tracking ID: "+str(int(first_object.id))+" tracking state: "+repr(first_object.tracking_state)+" / "+repr(first_object.action_state))
                    position = first_object.position
                    velocity = first_object.velocity
                    dimensions = first_object.dimensions
                    print(" 3D position: [{0},{1},{2}]\n Velocity: [{3},{4},{5}]\n 3D dimentions: [{6},{7},{8}]".format(position[0],position[1],position[2],velocity[0],velocity[1],velocity[2],dimensions[0],dimensions[1],dimensions[2]))
                    if first_object.mask.is_init():
                        print(" 2D mask available")

                    print(" Bounding Box 2D ")
                    bounding_box_2d = first_object.bounding_box_2d
                    for it in bounding_box_2d :
                        print("    "+str(it),end='')
                    x = bounding_box_2d[0][0]
                    y = bounding_box_2d[0][1]
                    w = bounding_box_2d[1][0] - bounding_box_2d[0][0]
                    h = bounding_box_2d[3][1] - bounding_box_2d[0][1]
                    print("\n Bounding Box 3D ")
                    bounding_box = first_object.bounding_box
                    for it in bounding_box :
                        print("    "+str(it),end='')
                    zed.retrieve_image(image_zed, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
                    zed.retrieve_image(depth_image_zed, sl.VIEW.DEPTH, sl.MEM.CPU, image_size)
                    # Retrieve the RGBA point cloud in half resolution
                    zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA, sl.MEM.CPU, image_size)

                    # To recover data from sl.Mat to use it with opencv, use the get_data() method
                    # It returns a numpy array that can be used as a matrix with opencv
                    image_ocv = image_zed.get_data()
                    depth_image_ocv = depth_image_zed.get_data()
                    image_ocv = cv2.resize(image_ocv, (1280,720), interpolation = inter)
                    img_ocv = cv2.rectangle(image_ocv,(int(x),int(y)),(int(x+w),int(y+h)),(0,255,0),2)
                    cv2.imshow("Image", image_ocv)
                    
                    cv2.imshow("bb",image_ocv)
                    print("image_shape:       .",img_ocv.shape)
                    cv2.imshow("Depth", depth_image_ocv)

                    key = cv2.waitKey(10)


    cv2.destroyAllWindows()
    zed.close()

    print("\nFINISH")

if __name__ == "__main__":
    main()

