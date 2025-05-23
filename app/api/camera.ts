import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create an axios instance with default config
const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor to add auth token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export interface Camera {
    id: number;
    name: string;
    ip_address: string;
    username: string;
    password: string;
    mall_id: number;
    location: string;
    created_at: string;
    homography_map?: {
        zones: Array<{
            name: string;
            points: Array<[number, number]>;
            objects: Array<{
                name: string;
                src_points: Array<[number, number]>;
                dst_points: Array<[number, number]>;
            }>;
        }>;
    };
    fov_zones?: {
        zones: Array<{
            name: string;
            points: Array<[number, number]>;
            type: string;
            description?: string;
        }>;
    };
}

export interface CameraCreate {
    name: string;
    ip_address: string;
    username: string;
    password: string;
    mall_id: number;
}

export interface HomographyMappingRequest {
    camera_id: number;
    zones: Array<{
        name: string;
        points: Array<[number, number]>;
        objects: Array<{
            name: string;
            src_points: Array<[number, number]>;
            dst_points: Array<[number, number]>;
        }>;
    }>;
}

export interface FOVZoneRequest {
    camera_id: number;
    zone: {
        name: string;
        points: Array<[number, number]>;
        type: string;
        description?: string;
    };
}

export const saveHomographyMappings = async (request: HomographyMappingRequest): Promise<Camera> => {
    try {
        const response = await api.post('/homography/save-mappings', request);
        return response.data.camera;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('Error saving homography mappings:', error.response?.data || error.message);
            throw new Error(error.response?.data?.detail || error.message);
        }
        throw error;
    }
};

export const updateFOVZone = async (request: FOVZoneRequest): Promise<Camera> => {
    try {
        const response = await api.post('/fov/update-zone', request);
        return response.data.camera;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('Error updating FOV zone:', error.response?.data || error.message);
            throw new Error(error.response?.data?.detail || error.message);
        }
        throw error;
    }
};

export const deleteFOVZone = async (cameraId: number, zoneName: string): Promise<Camera> => {
    try {
        const response = await api.delete(`/fov/delete-zone/${cameraId}/${zoneName}`);
        return response.data.camera;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error('Error deleting FOV zone:', error.response?.data || error.message);
            throw new Error(error.response?.data?.detail || error.message);
        }
        throw error;
    }
}; 