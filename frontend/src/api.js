import axios from 'axios';
const API_BASE_URL = "http://127.0.0.1:8000";

export const convertPdfToEpub = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await axios.post(`${API_BASE_URL}/convert`, formData, {
        responseType: 'blob',
    });
    return response.data;
};